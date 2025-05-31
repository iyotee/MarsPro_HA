"""L'intégration MarsHydro pour Home Assistant avec support Bluetooth BLE."""
import asyncio
import logging
import re
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.components import bluetooth

from .const import DOMAIN
from .api_marspro import MarsProAPI

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.LIGHT]

SCAN_INTERVAL = timedelta(seconds=30)


class MarsHydroDataUpdateCoordinator(DataUpdateCoordinator):
    """Coordinateur de données pour MarsHydro avec support Bluetooth BLE."""

    def __init__(self, hass: HomeAssistant, api: MarsProAPI) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
        )
        self.api = api
        self.devices = []
        self.bluetooth_devices = {}
        self.is_bluetooth_device = False

    async def _async_update_data(self):
        """Fetch data from API endpoint and detect devices."""
        try:
            _LOGGER.info("Fetching device data from MarsPro API...")
            
            # Récupérer la liste des appareils depuis l'API MarsPro
            devices = await self.api.get_all_devices()
            
            if not devices:
                _LOGGER.warning("No devices found via MarsPro API")
                return {"devices": [], "bluetooth_devices": {}}
            
            _LOGGER.info(f"Found {len(devices)} devices via MarsPro API")
            
            processed_devices = []
            bluetooth_count = 0
            
            # Traiter chaque appareil pour extraction PID et type
            for device in devices:
                device_name = device.get('name', '')
                device_id = device.get('id')
                
                if not device_id or not device_name:
                    _LOGGER.warning(f"Skipping device with missing ID or name: {device}")
                    continue
                
                # Extraire le PID depuis le nom
                pid_match = re.search(r'([A-F0-9]{12})$', device_name)
                if not pid_match:
                    _LOGGER.warning(f"Cannot extract PID from device name: {device_name}")
                    continue
                
                extracted_pid = pid_match.group(1)
                
                # Déterminer le type d'entité
                device_name_lower = device_name.lower()
                if any(keyword in device_name_lower for keyword in ['light', 'led', 'dimbox', 'lamp']):
                    entity_type = "light"
                elif any(keyword in device_name_lower for keyword in ['fan', 'ventil', 'exhaust']):
                    entity_type = "fan"
                else:
                    entity_type = "light"  # fallback vers light
                
                # Détecter si c'est un appareil Bluetooth
                is_bluetooth = not device.get('is_net_device', True)
                
                if is_bluetooth:
                    bluetooth_count += 1
                    self.is_bluetooth_device = True
                
                processed_device = {
                    'id': device_id,
                    'name': device_name,
                    'pid': extracted_pid,
                    'entity_type': entity_type,
                    'is_bluetooth': is_bluetooth,
                    'raw_data': device
                }
                
                processed_devices.append(processed_device)
                
                _LOGGER.info(
                    f"Processed device: {device_name} (ID: {device_id}, "
                    f"PID: {extracted_pid}, Type: {entity_type}, "
                    f"Bluetooth: {is_bluetooth})"
                )
            
            # Scanner Bluetooth si on a des appareils BLE
            if bluetooth_count > 0:
                _LOGGER.info(f"Found {bluetooth_count} Bluetooth devices, scanning BLE...")
                await self._scan_bluetooth_devices()
            
            self.devices = processed_devices
            
            return {
                "devices": processed_devices,
                "bluetooth_devices": self.bluetooth_devices
            }
            
        except Exception as err:
            _LOGGER.error(f"Error communicating with API: {err}")
            raise UpdateFailed(f"Error communicating with API: {err}")

    async def _scan_bluetooth_devices(self):
        """Scanner les appareils Bluetooth BLE MarsPro."""
        try:
            # Tenter import bleak pour scan direct si scanner HA non dispo
            try:
                from bleak import BleakScanner
                
                _LOGGER.info("Scanning Bluetooth BLE devices with Bleak...")
                devices = await BleakScanner.discover(timeout=10.0)
                
                self.bluetooth_devices = {}
                
                for device in devices:
                    if self._is_marspro_device(device):
                        device_name = device.name or f"MarsPro {device.address[-4:]}"
                        
                        self.bluetooth_devices[device.address] = {
                            'name': device_name,
                            'address': device.address,
                            'rssi': getattr(device, 'rssi', -50),
                            'device': device
                        }
                        
                        _LOGGER.info(f"Found MarsPro BLE device: {device_name} ({device.address})")
                
            except ImportError:
                _LOGGER.warning("Bleak not available, trying HA Bluetooth scanner...")
                
                # Essayer le scanner HA en fallback
                if hasattr(bluetooth, 'async_get_scanner'):
                    scanner = bluetooth.async_get_scanner(self.hass)
                    if scanner:
                        # Note: L'API exacte peut varier selon la version HA
                        _LOGGER.info("Using Home Assistant Bluetooth scanner")
                
        except Exception as e:
            _LOGGER.error(f"Bluetooth scan failed: {e}")

    def _is_marspro_device(self, device) -> bool:
        """Déterminer si un appareil BLE est un MarsPro."""
        device_name = (device.name or "").lower()
        device_addr = device.address.lower().replace(":", "")
        
        # Patterns MarsPro connus
        marspro_patterns = [
            "mars", "pro", "mh-", "dimbox", "led", "light", "grow"
        ]
        
        # Vérifier le nom
        for pattern in marspro_patterns:
            if pattern in device_name:
                return True
        
        # Vérifier si l'adresse MAC contient des PIDs connus
        for processed_device in self.devices:
            if processed_device.get('is_bluetooth') and processed_device.get('pid'):
                pid_fragment = processed_device['pid'][-6:].lower()  # 6 derniers chars
                if pid_fragment in device_addr:
                    return True
        
        return False

    def get_devices_by_type(self, entity_type: str):
        """Récupérer les appareils par type d'entité."""
        return [device for device in self.devices if device['entity_type'] == entity_type]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up MarsHydro from a config entry."""
    email = entry.data["email"]
    password = entry.data["password"]

    api = MarsProAPI(email, password)
    
    try:
        login_success = await api.login()
        if not login_success:
            _LOGGER.error("Failed to login to MarsPro API")
            return False
        _LOGGER.info("MarsHydro API connection successful")
    except Exception as e:
        _LOGGER.error(f"Failed to connect to MarsHydro API: {e}")
        return False

    coordinator = MarsHydroDataUpdateCoordinator(hass, api)
    
    # Fetch initial data
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "api": api,
    }

    # Setup platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
