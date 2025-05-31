"""Support pour les lumières MarsHydro avec modèle hybride BLE + Cloud."""
import asyncio
import json
import logging
from typing import Any

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ColorMode,
    LightEntity,
    LightEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up MarsHydro light based on a config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    entities = []

    # Attendre que le coordinateur ait des données
    if not coordinator.data:
        _LOGGER.warning("No coordinator data available")
        return

    devices = coordinator.data.get("devices", [])
    light_devices = [device for device in devices if device['entity_type'] == 'light']
    
    _LOGGER.info(f"Setting up {len(light_devices)} light entities")

    # Créer entités selon le type d'appareil (découvertes du modèle hybride)
    for device in light_devices:
        device_id = device['id']
        device_name = device['name']
        device_pid = device['pid']
        is_bluetooth = device['is_bluetooth']
        
        if is_bluetooth and device.get('requires_ble_connection'):
            # MODÈLE HYBRIDE: BLE + Cloud
            _LOGGER.info(f"Creating HYBRID entity for {device_name} (requires BLE connection)")
            
            hybrid_entity = MarsHydroHybridLight(
                coordinator, config_entry, device_id, device_name, device_pid
            )
            entities.append(hybrid_entity)
            
        elif not is_bluetooth:
            # MODÈLE CLOUD SEUL: WiFi/Ethernet
            _LOGGER.info(f"Creating CLOUD entity for {device_name} (WiFi/Ethernet)")
            
            cloud_entity = MarsHydroCloudLight(
                coordinator, config_entry, device_id, device_name, device_pid
            )
            entities.append(cloud_entity)
            
        else:
            # MODÈLE BLE SEUL: Bluetooth direct (si supporté)
            _LOGGER.info(f"Creating BLE entity for {device_name} (BLE only)")
            
            ble_entity = MarsHydroBluetoothLight(
                coordinator, config_entry, device_id, device_name, device_pid
            )
            entities.append(ble_entity)

    if entities:
        async_add_entities(entities, update_before_add=True)
        _LOGGER.info(f"Added {len(entities)} light entities to Home Assistant")
    else:
        _LOGGER.warning("No light entities to add")


class MarsHydroHybridLight(CoordinatorEntity, LightEntity):
    """Entité light MarsHydro HYBRIDE (BLE + Cloud).
    
    MODÈLE DÉCOUVERT:
    1. Établir connexion BLE avec l'appareil
    2. Envoyer commandes via Cloud API
    3. Les commandes transitent : Cloud → BLE → Appareil
    4. Maintenir connexion BLE active pour contrôle
    """

    _attr_color_mode = ColorMode.BRIGHTNESS
    _attr_supported_color_modes = {ColorMode.BRIGHTNESS}
    _attr_supported_features = LightEntityFeature.TRANSITION

    def __init__(self, coordinator, config_entry, device_id, device_name, device_pid):
        """Initialize the hybrid light."""
        super().__init__(coordinator)
        self._config_entry = config_entry
        self._device_id = device_id
        self._device_name = device_name
        self._device_pid = device_pid
        self._attr_unique_id = f"marspro_{device_id}_hybrid"
        self._is_on = False
        self._brightness = 255
        self._ble_connected = False

    @property
    def name(self) -> str:
        """Return the display name of this light."""
        return f"{self._device_name}"

    @property
    def is_on(self) -> bool:
        """Return true if light is on."""
        return self._is_on

    @property
    def brightness(self) -> int | None:
        """Return the brightness of this light between 0..255."""
        return self._brightness

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        # Disponible si BLE détecté OU si cloud API fonctionne
        has_ble = len(self.coordinator.bluetooth_devices) > 0
        has_cloud = self.coordinator.api is not None
        return has_ble or has_cloud

    @property
    def extra_state_attributes(self):
        """Return device specific state attributes."""
        attrs = {
            "device_id": self._device_id,
            "device_pid": self._device_pid,
            "control_mode": "hybrid_ble_cloud",
            "ble_connected": self._ble_connected,
        }
        
        # Ajouter infos BLE si disponibles
        for address, ble_info in self.coordinator.bluetooth_devices.items():
            if self._device_pid.lower() in address.lower().replace(":", ""):
                attrs.update({
                    "ble_address": address,
                    "ble_name": ble_info.get('name'),
                    "ble_rssi": ble_info.get('rssi'),
                })
                break
                
        return attrs

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on light using HYBRID model (BLE + Cloud)."""
        brightness = kwargs.get(ATTR_BRIGHTNESS)
        
        if brightness is not None:
            brightness_pct = int(brightness * 100 / 255)
        else:
            brightness_pct = 100

        _LOGGER.info(f"HYBRID: Turning on {self._device_name} at {brightness_pct}%")
        
        try:
            # ÉTAPE 1: Établir connexion BLE si nécessaire
            await self._ensure_ble_connection()
            
            # ÉTAPE 2: Envoyer commandes cloud (qui transitent via BLE)
            success = await self._send_hybrid_commands(True, brightness_pct)
            
            if success:
                self._is_on = True
                self._brightness = brightness if brightness is not None else 255
                self.async_write_ha_state()
                _LOGGER.info(f"HYBRID: Successfully turned on {self._device_name}")
            else:
                _LOGGER.error(f"HYBRID: Failed to turn on {self._device_name}")
                
        except Exception as e:
            _LOGGER.error(f"HYBRID: Error turning on {self._device_name}: {e}")

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off light using HYBRID model."""
        _LOGGER.info(f"HYBRID: Turning off {self._device_name}")
        
        try:
            # ÉTAPE 1: Établir connexion BLE si nécessaire
            await self._ensure_ble_connection()
            
            # ÉTAPE 2: Envoyer commande d'extinction via cloud
            success = await self._send_hybrid_commands(False, 0)
            
            if success:
                self._is_on = False
                self._brightness = 0
                self.async_write_ha_state()
                _LOGGER.info(f"HYBRID: Successfully turned off {self._device_name}")
            else:
                _LOGGER.error(f"HYBRID: Failed to turn off {self._device_name}")
                
        except Exception as e:
            _LOGGER.error(f"HYBRID: Error turning off {self._device_name}: {e}")

    async def _ensure_ble_connection(self):
        """S'assurer que la connexion BLE est établie."""
        try:
            client = await self.coordinator.establish_ble_connection(self._device_pid)
            self._ble_connected = client is not None
            
            if self._ble_connected:
                _LOGGER.debug(f"BLE connection active for {self._device_pid}")
            else:
                _LOGGER.warning(f"BLE connection failed for {self._device_pid}")
                
        except Exception as e:
            _LOGGER.error(f"BLE connection error for {self._device_pid}: {e}")
            self._ble_connected = False

    async def _send_hybrid_commands(self, is_on: bool, brightness_pct: int) -> bool:
        """Envoyer commandes via cloud avec BLE connecté."""
        try:
            api = self.coordinator.api
            
            # Commande addDevice (déverrouillage si nécessaire)
            add_payload = {
                "deviceName": f"MH-DIMBOX-{self._device_pid}",
                "bluetoothName": self._device_pid,
                "productModelCode": "MZL001",
                "deviceSerialNum": self._device_pid,
                "pcode": 2002
            }
            
            add_response = await api._make_request("/api/android/udm/addDevice/v1", add_payload)
            
            if add_response and add_response.get('code') == '000':
                device_id = add_response.get('data', {}).get('id', self._device_id)
                _LOGGER.debug(f"addDevice successful, using device_id: {device_id}")
            else:
                device_id = self._device_id
                _LOGGER.debug(f"addDevice failed, using existing device_id: {device_id}")
            
            # Petit délai pour synchronisation
            await asyncio.sleep(1)
            
            # Commande d'activation
            if is_on:
                activation_command = {
                    "method": "setDeviceActive",
                    "pid": self._device_pid,
                    "deviceId": device_id,
                    "msgId": "ha_active",
                    "msg": "1",
                    "code": 200,
                    "active": True
                }
                
                activation_payload = {"data": json.dumps(activation_command)}
                activation_response = await api._make_request("/api/upData/device", activation_payload)
                
                if not activation_response or activation_response.get('code') != '000':
                    _LOGGER.warning(f"Device activation failed: {activation_response}")
                
                await asyncio.sleep(1)
            
            # Commande de luminosité/contrôle
            if is_on and brightness_pct > 0:
                brightness_command = {
                    "method": "setBrightness",
                    "pid": self._device_pid,
                    "deviceId": device_id,
                    "msgId": "ha_brightness",
                    "msg": "1",
                    "code": 200,
                    "brightness": brightness_pct
                }
            else:
                # Extinction
                brightness_command = {
                    "method": "setDeviceActive",
                    "pid": self._device_pid,
                    "deviceId": device_id,
                    "msgId": "ha_off",
                    "msg": "1",
                    "code": 200,
                    "active": False
                }
            
            control_payload = {"data": json.dumps(brightness_command)}
            control_response = await api._make_request("/api/upData/device", control_payload)
            
            if control_response and control_response.get('code') == '000':
                _LOGGER.debug(f"Control command successful: {brightness_command['method']}")
                return True
            else:
                _LOGGER.error(f"Control command failed: {control_response}")
                return False
                
        except Exception as e:
            _LOGGER.error(f"Hybrid command error: {e}")
            return False


class MarsHydroCloudLight(CoordinatorEntity, LightEntity):
    """Entité light MarsHydro Cloud seul (WiFi/Ethernet)."""

    _attr_color_mode = ColorMode.BRIGHTNESS
    _attr_supported_color_modes = {ColorMode.BRIGHTNESS}
    _attr_supported_features = LightEntityFeature.TRANSITION

    def __init__(self, coordinator, config_entry, device_id, device_name, device_pid):
        """Initialize the cloud light."""
        super().__init__(coordinator)
        self._config_entry = config_entry
        self._device_id = device_id
        self._device_name = device_name
        self._device_pid = device_pid
        self._attr_unique_id = f"marspro_{device_id}_cloud"
        self._is_on = False
        self._brightness = 255

    @property
    def name(self) -> str:
        """Return the display name of this light."""
        return f"{self._device_name} (Cloud)"

    @property
    def is_on(self) -> bool:
        """Return true if light is on."""
        return self._is_on

    @property
    def brightness(self) -> int | None:
        """Return the brightness of this light between 0..255."""
        return self._brightness

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on light via cloud only."""
        brightness = kwargs.get(ATTR_BRIGHTNESS)
        
        if brightness is not None:
            brightness_pct = int(brightness * 100 / 255)
        else:
            brightness_pct = 100

        _LOGGER.info(f"CLOUD: Turning on {self._device_name} at {brightness_pct}%")
        
        try:
            # Utiliser la méthode control_device_by_pid
            success = await self.coordinator.api.control_device_by_pid(self._device_pid, True, brightness_pct)
            
            if success:
                self._is_on = True
                self._brightness = brightness if brightness is not None else 255
                self.async_write_ha_state()
                _LOGGER.info(f"CLOUD: Successfully turned on {self._device_name}")
            else:
                _LOGGER.error(f"CLOUD: Failed to turn on {self._device_name}")
                
        except Exception as e:
            _LOGGER.error(f"CLOUD: Error turning on {self._device_name}: {e}")

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off light via cloud only."""
        _LOGGER.info(f"CLOUD: Turning off {self._device_name}")
        
        try:
            success = await self.coordinator.api.control_device_by_pid(self._device_pid, False, 0)
            
            if success:
                self._is_on = False
                self._brightness = 0
                self.async_write_ha_state()
                _LOGGER.info(f"CLOUD: Successfully turned off {self._device_name}")
            else:
                _LOGGER.error(f"CLOUD: Failed to turn off {self._device_name}")
                
        except Exception as e:
            _LOGGER.error(f"CLOUD: Error turning off {self._device_name}: {e}")


class MarsHydroBluetoothLight(CoordinatorEntity, LightEntity):
    """Entité light MarsHydro BLE direct (expérimental)."""

    _attr_color_mode = ColorMode.BRIGHTNESS
    _attr_supported_color_modes = {ColorMode.BRIGHTNESS}
    _attr_supported_features = LightEntityFeature.TRANSITION

    def __init__(self, coordinator, config_entry, device_id, device_name, device_pid):
        """Initialize the Bluetooth light."""
        super().__init__(coordinator)
        self._config_entry = config_entry
        self._device_id = device_id
        self._device_name = device_name
        self._device_pid = device_pid
        self._attr_unique_id = f"marspro_{device_id}_ble"
        self._is_on = False
        self._brightness = 255

    @property
    def name(self) -> str:
        """Return the display name of this light."""
        return f"{self._device_name} (BLE Direct)"

    @property
    def is_on(self) -> bool:
        """Return true if light is on."""
        return self._is_on

    @property
    def brightness(self) -> int | None:
        """Return the brightness of this light between 0..255."""
        return self._brightness

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return len(self.coordinator.bluetooth_devices) > 0

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on light via Bluetooth BLE direct."""
        brightness = kwargs.get(ATTR_BRIGHTNESS, 255)
        brightness_pct = int(brightness * 100 / 255)
        
        _LOGGER.info(f"BLE DIRECT: Turning on {self._device_name} at {brightness_pct}%")
        
        try:
            # Protocole BLE direct (expérimental)
            success = await self._ble_direct_control(True, brightness_pct)
            
            if success:
                self._is_on = True
                self._brightness = brightness
                self.async_write_ha_state()
                _LOGGER.info(f"BLE DIRECT: Successfully turned on {self._device_name}")
            else:
                _LOGGER.warning(f"BLE DIRECT: Control failed for {self._device_name}")
                
        except Exception as e:
            _LOGGER.error(f"BLE DIRECT: Error turning on {self._device_name}: {e}")

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off light via Bluetooth BLE direct."""
        _LOGGER.info(f"BLE DIRECT: Turning off {self._device_name}")
        
        try:
            success = await self._ble_direct_control(False, 0)
            
            if success:
                self._is_on = False
                self._brightness = 0
                self.async_write_ha_state()
                _LOGGER.info(f"BLE DIRECT: Successfully turned off {self._device_name}")
            else:
                _LOGGER.warning(f"BLE DIRECT: Control failed for {self._device_name}")
                
        except Exception as e:
            _LOGGER.error(f"BLE DIRECT: Error turning off {self._device_name}: {e}")

    async def _ble_direct_control(self, is_on: bool, brightness_pct: int) -> bool:
        """Contrôle BLE direct (expérimental)."""
        try:
            client = await self.coordinator.establish_ble_connection(self._device_pid)
            
            if not client:
                return False
            
            # Protocoles BLE à tester
            if is_on:
                brightness_val = int(brightness_pct * 255 / 100)
                protocols = [
                    bytes([0x01, brightness_val]),  # Simple on + brightness
                    bytes([0x55, 0xAA, 0x01, brightness_val, 0xFF]),  # Avec header
                ]
            else:
                protocols = [
                    bytes([0x00, 0x00]),  # Simple off
                    bytes([0x55, 0xAA, 0x00, 0x00, 0xFF]),  # Off avec header
                ]
            
            # Obtenir caractéristiques d'écriture
            services = await client.get_services()
            write_chars = []
            
            for service in services.services:
                for char in service.characteristics:
                    if "write" in char.properties:
                        write_chars.append(char)
            
            if not write_chars:
                _LOGGER.warning(f"No writable characteristics found for {self._device_pid}")
                return False
            
            # Tester les protocoles
            for char in write_chars[:2]:  # Tester les 2 premières caractéristiques
                for protocol in protocols:
                    try:
                        await client.write_gatt_char(char.uuid, protocol, response=False)
                        _LOGGER.debug(f"BLE protocol sent: {protocol.hex()} to {char.uuid}")
                        await asyncio.sleep(0.5)
                    except Exception as e:
                        _LOGGER.debug(f"BLE protocol failed: {e}")
            
            # Note: Pas de retour fiable pour BLE direct
            return True
            
        except Exception as e:
            _LOGGER.error(f"BLE direct control error: {e}")
            return False
