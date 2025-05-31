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
        self.ble_scan_failed = False

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
            if bluetooth_count > 0 and not self.ble_scan_failed:
                _LOGGER.info(f"Found {bluetooth_count} Bluetooth devices, scanning BLE...")
                _LOGGER.info("HYBRID MODEL: These devices need BLE connection + Cloud commands")
                await self._scan_bluetooth_devices()
            elif self.ble_scan_failed:
                _LOGGER.warning("BLE scan previously failed, skipping BLE detection")
            
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
            # PRIORITÉ 1: Essayer scanner Home Assistant d'abord
            _LOGGER.info("Trying Home Assistant Bluetooth scanner first...")
            
            try:
                # Utiliser le scanner HA Bluetooth si disponible
                if hasattr(self.hass.components, 'bluetooth'):
                    bluetooth_component = self.hass.components.bluetooth
                    
                    # Méthode moderne HA 2024+
                    if hasattr(bluetooth_component, 'async_discovered_service_info'):
                        discovered = bluetooth_component.async_discovered_service_info(self.hass)
                        
                        for device_info in discovered:
                            device_name = device_info.name or ""
                            device_address = device_info.address
                            
                            if self._is_marspro_device_by_name_addr(device_name, device_address):
                                _LOGGER.info(f"Found MarsPro via HA Bluetooth: {device_name} ({device_address})")
                                
                                self.bluetooth_devices[device_address] = {
                                    'name': device_name,
                                    'address': device_address,
                                    'rssi': getattr(device_info, 'rssi', -50),
                                    'is_reachable': True,
                                    'via_ha_bluetooth': True
                                }
                                
                                await self._correlate_ble_with_cloud_device_by_addr(device_address, device_name)
                        
                        if self.bluetooth_devices:
                            _LOGGER.info(f"HA Bluetooth found {len(self.bluetooth_devices)} MarsPro devices")
                            return
                
            except Exception as ha_bt_error:
                _LOGGER.warning(f"HA Bluetooth scanner failed: {ha_bt_error}")
            
            # PRIORITÉ 2: Fallback vers Bleak
            _LOGGER.info("Falling back to Bleak scanner...")
            
            try:
                from bleak import BleakScanner
                
                _LOGGER.info("Scanning with Bleak (20s timeout)...")
                _LOGGER.info("Looking for MarsPro patterns: MH-DIMBOX, 345F45EC73CC...")
                
                devices = await BleakScanner.discover(timeout=20.0)
                
                for device in devices:
                    if self._is_marspro_device(device):
                        device_name = device.name or f"MarsPro {device.address[-4:]}"
                        
                        self.bluetooth_devices[device.address] = {
                            'name': device_name,
                            'address': device.address,
                            'rssi': getattr(device, 'rssi', -50),
                            'device': device,
                            'is_reachable': True,
                            'via_bleak': True
                        }
                        
                        _LOGGER.info(f"Found MarsPro BLE device: {device_name} ({device.address})")
                        
                        # Tenter de correlate avec les appareils cloud
                        await self._correlate_ble_with_cloud_device(device)
                
                if not self.bluetooth_devices:
                    _LOGGER.warning("No MarsPro BLE devices found with Bleak!")
                    _LOGGER.warning("Device may not be in pairing mode")
                    self.ble_scan_failed = True
                
            except ImportError:
                _LOGGER.error("Bleak not available! Install: pip install bleak")
                self.ble_scan_failed = True
            except Exception as bleak_error:
                _LOGGER.error(f"Bleak scan failed: {bleak_error}")
                self.ble_scan_failed = True
                
        except Exception as e:
            _LOGGER.error(f"Bluetooth scan completely failed: {e}")
            self.ble_scan_failed = True

    def _is_marspro_device_by_name_addr(self, device_name: str, device_address: str) -> bool:
        """Vérifier si un appareil est MarsPro par nom et adresse."""
        device_name_lower = device_name.lower()
        device_addr_clean = device_address.lower().replace(":", "")
        
        # Patterns MarsPro découverts
        name_patterns = ["mh-dimbox", "mars", "pro", "dimbox", "345f45ec73cc"]
        
        # Vérifier nom
        for pattern in name_patterns:
            if pattern in device_name_lower:
                return True
        
        # Vérifier correspondance PID dans adresse
        for device in self.devices:
            if device.get('is_bluetooth') and device.get('pid'):
                pid = device['pid'].lower()
                if pid in device_addr_clean:
                    return True
        
        return False

    async def _correlate_ble_with_cloud_device_by_addr(self, ble_address: str, ble_name: str):
        """Corréler par adresse et nom."""
        ble_addr_clean = ble_address.replace(":", "").lower()
        ble_name_lower = ble_name.lower()
        
        for cloud_device in self.devices:
            if cloud_device.get('is_bluetooth') and cloud_device.get('pid'):
                cloud_pid = cloud_device['pid'].lower()
                
                # Pattern découvert: 34:5F:45:EC:73:CE ≈ 345F45EC73CC
                if cloud_pid in ble_addr_clean or "dimbox" in ble_name_lower:
                    _LOGGER.info(f"CORRELATED: BLE {ble_name} ({ble_address}) ↔ Cloud {cloud_device['name']}")
                    cloud_device['ble_address'] = ble_address
                    cloud_device['ble_name'] = ble_name
                    return

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
        """Établir connexion BLE pour appareil hybride (MÉTHODE AMÉLIORÉE)."""
        try:
            # Trouver l'appareil correspondant
            target_device = None
            for device in self.devices:
                if device.get('pid') == device_pid:
                    target_device = device
                    break
            
            if not target_device:
                _LOGGER.error(f"No device found for PID {device_pid}")
                return None
            
            # Vérifier si on a une adresse BLE
            ble_address = target_device.get('ble_address')
            if not ble_address:
                _LOGGER.warning(f"No BLE address found for PID {device_pid}")
                _LOGGER.warning("Device may not be in pairing mode or not detected by BLE scan")
                return None
            
            # Si déjà connecté, retourner la connexion existante
            if ble_address in self.ble_connections:
                client = self.ble_connections[ble_address]
                try:
                    if await client.is_connected():
                        _LOGGER.debug(f"Reusing existing BLE connection for {device_pid}")
                        return client
                    else:
                        # Nettoyer connexion morte
                        del self.ble_connections[ble_address]
                except:
                    del self.ble_connections[ble_address]
            
            # Établir nouvelle connexion avec timeout
            _LOGGER.info(f"Establishing BLE connection to {target_device['name']} ({ble_address})")
            
            try:
                from bleak import BleakClient
                
                client = BleakClient(ble_address, timeout=30.0)
                
                # Tentative de connexion avec retry
                for attempt in range(3):
                    try:
                        _LOGGER.info(f"BLE connection attempt {attempt + 1}/3 for {device_pid}")
                        await client.connect()
                        
                        if await client.is_connected():
                            self.ble_connections[ble_address] = client
                            _LOGGER.info(f"✅ BLE connection established for {device_pid}")
                            return client
                        
                    except Exception as connect_error:
                        _LOGGER.warning(f"BLE connection attempt {attempt + 1} failed: {connect_error}")
                        if attempt < 2:  # Retry
                            await asyncio.sleep(2)
                            continue
                        else:
                            raise connect_error
                
                _LOGGER.error(f"❌ All BLE connection attempts failed for {device_pid}")
                return None
                
            except ImportError:
                _LOGGER.error("Bleak not available for BLE connection")
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
                    try:
                        if await client.is_connected():
                            await client.disconnect()
                    except:
                        pass
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
