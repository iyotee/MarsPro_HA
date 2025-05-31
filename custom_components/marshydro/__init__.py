"""L'intégration MarsHydro pour Home Assistant avec support Bluetooth BLE."""
import asyncio
import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.components import bluetooth

from .const import DOMAIN
from .api_marspro import MarsProAPI

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.LIGHT, Platform.SWITCH]

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
        self.bluetooth_devices = {}
        self.is_bluetooth_device = False

    async def _async_update_data(self):
        """Fetch data from API endpoint or Bluetooth."""
        try:
            # Essayer d'abord l'API cloud
            light_data = await self.api.get_lightdata()
            fan_data = await self.api.get_fandata()
            
            # Détecter si c'est un appareil Bluetooth
            if light_data and light_data.get('connection_type') == 'bluetooth':
                self.is_bluetooth_device = True
                _LOGGER.info("Device detected as Bluetooth BLE")
                
                # Scanner les appareils Bluetooth BLE
                await self._scan_bluetooth_devices()
            
            return {
                "light": light_data,
                "fan": fan_data,
                "bluetooth_devices": self.bluetooth_devices
            }
            
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}")

    async def _scan_bluetooth_devices(self):
        """Scanner les appareils Bluetooth BLE MarsPro."""
        try:
            # Utiliser le scanner Bluetooth intégré de Home Assistant
            scanner = bluetooth.async_get_scanner(self.hass)
            
            if not scanner:
                _LOGGER.warning("Bluetooth scanner not available")
                return
            
            # Scanner pendant 10 secondes
            devices = await scanner.async_discover(timeout=10.0)
            
            marspro_devices = []
            for device in devices:
                if self._is_marspro_device(device):
                    marspro_devices.append(device)
                    _LOGGER.info(f"Found MarsPro BLE device: {device.name} ({device.address})")
            
            self.bluetooth_devices = {
                device.address: {
                    'name': device.name or f"MarsPro {device.address[-4:]}",
                    'address': device.address,
                    'rssi': getattr(device, 'rssi', -50),
                    'device': device
                }
                for device in marspro_devices
            }
            
        except Exception as e:
            _LOGGER.error(f"Bluetooth scan failed: {e}")

    def _is_marspro_device(self, device) -> bool:
        """Déterminer si un appareil BLE est un MarsPro."""
        device_name = (device.name or "").lower()
        device_addr = device.address.lower()
        
        # Patterns MarsPro connus
        marspro_patterns = [
            "mars", "pro", "mh-", "dimbox", "345f45ec73cc",
            "led", "light", "grow"
        ]
        
        # Vérifier le nom
        for pattern in marspro_patterns:
            if pattern in device_name:
                return True
        
        # Vérifier l'adresse MAC (si elle contient des fragments du PID)
        if "345f45" in device_addr.replace(":", ""):
            return True
        
        return False


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up MarsHydro from a config entry."""
    email = entry.data["email"]
    password = entry.data["password"]

    api = MarsProAPI(email, password)
    
    try:
        await api.login()
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
