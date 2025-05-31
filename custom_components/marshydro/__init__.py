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
    """Coordinateur de données pour MarsHydro avec support Bluetooth BLE.
    
    DÉCOUVERTE MODÈLE HYBRIDE:
    - App MarsPro utilise Cloud API + Connexion BLE simultanée
    - Les commandes transitent par : Cloud → BLE → Appareil
    - L'appareil doit être connecté en BLE ET recevoir commandes cloud
    - Nom BLE: "MH-DIMBOX", Adresse: 34:5F:45:EC:73:CE ≈ PID 345F45EC73CC
    """

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
        self.ble_connections = {}  # Tracking des connexions BLE actives
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
                
                # Détecter si c'est un appareil Bluetooth (modèle hybride)
                is_bluetooth = not device.get('is_net_device', True)
                
                if is_bluetooth:
                    bluetooth_count += 1
                    self.is_bluetooth_device = True
                    _LOGGER.info(f"Device {device_name} requires HYBRID BLE+Cloud control")
                
                processed_device = {
                    'id': device_id,
                    'name': device_name,
                    'pid': extracted_pid,
                    'entity_type': entity_type,
                    'is_bluetooth': is_bluetooth,
                    'requires_ble_connection': is_bluetooth,  # Nouvelle propriété
                    'raw_data': device
                }
                
                processed_devices.append(processed_device)
                
                _LOGGER.info(
                    f"Processed device: {device_name} (ID: {device_id}, "
                    f"PID: {extracted_pid}, Type: {entity_type}, "
                    f"Bluetooth: {is_bluetooth})"
                )
            
            # Scanner Bluetooth si on a des appareils BLE (modèle hybride)
            if bluetooth_count > 0:
                _LOGGER.info(f"Found {bluetooth_count} Bluetooth devices, scanning BLE...")
                _LOGGER.info("HYBRID MODEL: These devices need BLE connection + Cloud commands")
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
        """Scanner les appareils Bluetooth BLE MarsPro avec patterns découverts."""
        try:
            # Tenter import bleak pour scan direct si scanner HA non dispo
            try:
                from bleak import BleakScanner
                
                _LOGGER.info("Scanning Bluetooth BLE devices with Bleak...")
                _LOGGER.info("Looking for MarsPro patterns: MH-DIMBOX, 345F45EC73CC...")
                
                devices = await BleakScanner.discover(timeout=15.0)
                
                self.bluetooth_devices = {}
                
                for device in devices:
                    if self._is_marspro_device(device):
                        device_name = device.name or f"MarsPro {device.address[-4:]}"
                        
                        self.bluetooth_devices[device.address] = {
                            'name': device_name,
                            'address': device.address,
                            'rssi': getattr(device, 'rssi', -50),
                            'device': device,
                            'is_reachable': True  # Pour tracking connexion
                        }
                        
                        _LOGGER.info(f"Found MarsPro BLE device: {device_name} ({device.address})")
                        
                        # Tenter de correlate avec les appareils cloud
                        await self._correlate_ble_with_cloud_device(device)
                
                if not self.bluetooth_devices:
                    _LOGGER.warning("No MarsPro BLE devices found!")
                    _LOGGER.warning("Make sure device is in pairing mode (disconnect from MarsPro app)")
                
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

    async def _correlate_ble_with_cloud_device(self, ble_device):
        """Corréler appareil BLE avec appareil cloud basé sur nos découvertes."""
        ble_addr = ble_device.address.replace(":", "").lower()
        ble_name = (ble_device.name or "").lower()
        
        # Pattern découvert: 34:5F:45:EC:73:CE ≈ 345F45EC73CC (PID)
        for cloud_device in self.devices:
            if cloud_device.get('is_bluetooth') and cloud_device.get('pid'):
                cloud_pid = cloud_device['pid'].lower()
                
                # Méthode 1: Correspondance directe PID ↔ Adresse MAC
                if cloud_pid in ble_addr or ble_addr.replace(":", "") in cloud_pid:
                    _LOGGER.info(f"CORRELATED: BLE {ble_device.name} ↔ Cloud {cloud_device['name']}")
                    cloud_device['ble_address'] = ble_device.address
                    cloud_device['ble_device'] = ble_device
                    return
                
                # Méthode 2: Pattern nom (MH-DIMBOX avec PID)
                if "dimbox" in ble_name and cloud_pid in cloud_device['name'].lower():
                    _LOGGER.info(f"CORRELATED by name: BLE {ble_device.name} ↔ Cloud {cloud_device['name']}")
                    cloud_device['ble_address'] = ble_device.address
                    cloud_device['ble_device'] = ble_device
                    return

    def _is_marspro_device(self, device) -> bool:
        """Déterminer si un appareil BLE est un MarsPro avec patterns découverts."""
        device_name = (device.name or "").lower()
        device_addr = device.address.lower().replace(":", "")
        
        # Patterns MarsPro découverts
        marspro_patterns = [
            "mh-dimbox",  # Pattern principal découvert
            "mars", "pro", "mh-", "dimbox", "led", "light", "grow"
        ]
        
        # Vérifier le nom
        for pattern in marspro_patterns:
            if pattern in device_name:
                _LOGGER.debug(f"MarsPro device detected by name pattern '{pattern}': {device.name}")
                return True
        
        # Vérifier correspondance avec PIDs connus des appareils cloud
        for processed_device in self.devices:
            if processed_device.get('is_bluetooth') and processed_device.get('pid'):
                cloud_pid = processed_device['pid'].lower()
                
                # Pattern découvert: 345F45EC73CC ≈ 34:5F:45:EC:73:CE
                if cloud_pid in device_addr or any(
                    cloud_pid[i:i+2] in device_addr for i in range(0, len(cloud_pid), 2)
                ):
                    _LOGGER.debug(f"MarsPro device detected by PID correlation: {device.name} ↔ {cloud_pid}")
                    return True
        
        return False

    def get_devices_by_type(self, entity_type: str):
        """Récupérer les appareils par type d'entité."""
        return [device for device in self.devices if device['entity_type'] == entity_type]

    async def establish_ble_connection(self, device_pid: str):
        """Établir connexion BLE pour appareil hybride (NOUVELLE MÉTHODE)."""
        try:
            from bleak import BleakClient
            
            # Trouver l'appareil correspondant
            target_device = None
            for device in self.devices:
                if device.get('pid') == device_pid and device.get('ble_address'):
                    target_device = device
                    break
            
            if not target_device:
                _LOGGER.error(f"No BLE device found for PID {device_pid}")
                return None
            
            ble_address = target_device['ble_address']
            
            # Si déjà connecté, retourner la connexion existante
            if ble_address in self.ble_connections:
                client = self.ble_connections[ble_address]
                if await client.is_connected():
                    return client
                else:
                    # Nettoyer connexion morte
                    del self.ble_connections[ble_address]
            
            # Établir nouvelle connexion
            _LOGGER.info(f"Establishing BLE connection to {target_device['name']} ({ble_address})")
            
            client = BleakClient(ble_address)
            await client.connect()
            
            if await client.is_connected():
                self.ble_connections[ble_address] = client
                _LOGGER.info(f"BLE connection established for {device_pid}")
                return client
            else:
                _LOGGER.error(f"Failed to establish BLE connection for {device_pid}")
                return None
                
        except Exception as e:
            _LOGGER.error(f"BLE connection error for {device_pid}: {e}")
            return None

    async def release_ble_connection(self, device_pid: str):
        """Libérer connexion BLE."""
        try:
            # Trouver l'adresse BLE
            target_device = None
            for device in self.devices:
                if device.get('pid') == device_pid and device.get('ble_address'):
                    target_device = device
                    break
            
            if target_device:
                ble_address = target_device['ble_address']
                if ble_address in self.ble_connections:
                    client = self.ble_connections[ble_address]
                    if await client.is_connected():
                        await client.disconnect()
                    del self.ble_connections[ble_address]
                    _LOGGER.info(f"BLE connection released for {device_pid}")
                    
        except Exception as e:
            _LOGGER.error(f"Error releasing BLE connection for {device_pid}: {e}")


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
    except Exception as err:
        _LOGGER.error(f"Failed to connect to MarsPro API: {err}")
        return False

    coordinator = MarsHydroDataUpdateCoordinator(hass, api)

    # Fetch initial data so we have data when entities subscribe
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    # Libérer toutes les connexions BLE
    for ble_address, client in coordinator.ble_connections.items():
        try:
            if await client.is_connected():
                await client.disconnect()
        except Exception as e:
            _LOGGER.error(f"Error disconnecting BLE device {ble_address}: {e}")
    
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
