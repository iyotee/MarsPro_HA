"""Support pour les lumières MarsHydro avec Bluetooth BLE."""
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
from homeassistant.components import bluetooth

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up MarsHydro light based on a config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    api = hass.data[DOMAIN][config_entry.entry_id]["api"]

    entities = []

    # Entité principale (cloud/WiFi)
    if coordinator.data and coordinator.data.get("light"):
        entities.append(MarsHydroLight(coordinator, api, config_entry))

    # Entités Bluetooth BLE
    if coordinator.is_bluetooth_device and coordinator.bluetooth_devices:
        for mac_address, device_info in coordinator.bluetooth_devices.items():
            entities.append(
                MarsHydroBluetoothLight(
                    coordinator, api, config_entry, mac_address, device_info
                )
            )

    async_add_entities(entities, update_before_add=True)


class MarsHydroLight(CoordinatorEntity, LightEntity):
    """Entité light MarsHydro (cloud/WiFi)."""

    _attr_color_mode = ColorMode.BRIGHTNESS
    _attr_supported_color_modes = {ColorMode.BRIGHTNESS}
    _attr_supported_features = LightEntityFeature.TRANSITION

    def __init__(self, coordinator, api, config_entry):
        """Initialize the light."""
        super().__init__(coordinator)
        self.api = api
        self._config_entry = config_entry
        self._attr_unique_id = f"{DOMAIN}_{config_entry.entry_id}_light"

    @property
    def name(self) -> str:
        """Return the display name of this light."""
        if self.coordinator.data and self.coordinator.data.get("light"):
            device_name = self.coordinator.data["light"].get("deviceName", "MarsHydro Light")
            return device_name
        return "MarsHydro Light"

    @property
    def is_on(self) -> bool:
        """Return true if light is on."""
        if self.coordinator.data and self.coordinator.data.get("light"):
            data = self.coordinator.data["light"]
            # Vérifier plusieurs champs possibles pour l'état
            return (
                data.get("stat") == 1 or
                data.get("on") == 1 or
                data.get("switch") == 1 or
                data.get("isOn", False)
            )
        return False

    @property
    def brightness(self) -> int | None:
        """Return the brightness of this light between 0..255."""
        if self.coordinator.data and self.coordinator.data.get("light"):
            data = self.coordinator.data["light"]
            # Vérifier plusieurs champs possibles pour la luminosité
            pwm = (
                data.get("pwm") or
                data.get("brightness") or
                data.get("lastBright") or
                100
            )
            # Convertir de pourcentage (0-100) vers HA (0-255)
            return int(pwm * 255 / 100)
        return 255

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Instruct the light to turn on."""
        brightness = kwargs.get(ATTR_BRIGHTNESS)
        
        if brightness is not None:
            # Convertir de HA (0-255) vers pourcentage (0-100)
            brightness_pct = int(brightness * 100 / 255)
        else:
            brightness_pct = 100

        _LOGGER.info(f"Turning on light with brightness {brightness_pct}%")
        
        try:
            # Essayer le contrôle hybride (cloud + BLE)
            if hasattr(self.api, 'control_device_hybrid'):
                success = await self.api.control_device_hybrid(True, brightness_pct)
            else:
                # Fallback vers l'API standard
                await self.api.set_brightness(brightness_pct)
                success = True
            
            if success:
                await self.coordinator.async_request_refresh()
            else:
                _LOGGER.error("Failed to turn on light")
                
        except Exception as e:
            _LOGGER.error(f"Error turning on light: {e}")

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Instruct the light to turn off."""
        _LOGGER.info("Turning off light")
        
        try:
            # Essayer le contrôle hybride (cloud + BLE)
            if hasattr(self.api, 'control_device_hybrid'):
                success = await self.api.control_device_hybrid(False, 0)
            else:
                # Fallback vers toggle_switch
                await self.api.toggle_switch(True, "")
                success = True
            
            if success:
                await self.coordinator.async_request_refresh()
            else:
                _LOGGER.error("Failed to turn off light")
                
        except Exception as e:
            _LOGGER.error(f"Error turning off light: {e}")


class MarsHydroBluetoothLight(CoordinatorEntity, LightEntity):
    """Entité light MarsHydro Bluetooth BLE directe."""

    _attr_color_mode = ColorMode.BRIGHTNESS
    _attr_supported_color_modes = {ColorMode.BRIGHTNESS}
    _attr_supported_features = LightEntityFeature.TRANSITION

    def __init__(self, coordinator, api, config_entry, mac_address, device_info):
        """Initialize the Bluetooth light."""
        super().__init__(coordinator)
        self.api = api
        self._config_entry = config_entry
        self._mac_address = mac_address
        self._device_info = device_info
        self._attr_unique_id = f"{DOMAIN}_{mac_address.replace(':', '')}_ble_light"
        self._is_on = False
        self._brightness = 255

    @property
    def name(self) -> str:
        """Return the display name of this light."""
        return f"{self._device_info['name']} (BLE)"

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
        # Vérifier la disponibilité Bluetooth
        return self._mac_address in self.coordinator.bluetooth_devices

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Instruct the light to turn on via Bluetooth BLE."""
        brightness = kwargs.get(ATTR_BRIGHTNESS, 255)
        brightness_pct = int(brightness * 100 / 255)
        
        _LOGGER.info(f"Turning on BLE light {self._mac_address} with brightness {brightness_pct}%")
        
        try:
            success = await self._control_ble_device(True, brightness_pct)
            
            if success:
                self._is_on = True
                self._brightness = brightness
                self.async_write_ha_state()
            else:
                _LOGGER.error(f"Failed to turn on BLE light {self._mac_address}")
                
        except Exception as e:
            _LOGGER.error(f"Error turning on BLE light {self._mac_address}: {e}")

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Instruct the light to turn off via Bluetooth BLE."""
        _LOGGER.info(f"Turning off BLE light {self._mac_address}")
        
        try:
            success = await self._control_ble_device(False, 0)
            
            if success:
                self._is_on = False
                self.async_write_ha_state()
            else:
                _LOGGER.error(f"Failed to turn off BLE light {self._mac_address}")
                
        except Exception as e:
            _LOGGER.error(f"Error turning off BLE light {self._mac_address}: {e}")

    async def _control_ble_device(self, on: bool, brightness_pct: int) -> bool:
        """Contrôler l'appareil directement via Bluetooth BLE."""
        try:
            # Utiliser le scanner Bluetooth de Home Assistant
            ble_device = bluetooth.async_ble_device_from_address(self.hass, self._mac_address)
            
            if not ble_device:
                _LOGGER.error(f"BLE device {self._mac_address} not found")
                return False

            # Utiliser la méthode BLE de l'API si disponible
            if hasattr(self.api, '_ble_control_device'):
                self.api.ble_device = ble_device
                return await self.api._ble_control_device(on, brightness_pct)
            else:
                # Implémentation BLE directe simplifiée
                return await self._simple_ble_control(ble_device, on, brightness_pct)
                
        except Exception as e:
            _LOGGER.error(f"BLE control failed: {e}")
            return False

    async def _simple_ble_control(self, ble_device, on: bool, brightness_pct: int) -> bool:
        """Implémentation BLE directe simplifiée."""
        try:
            from bleak import BleakClient
            
            async with BleakClient(ble_device.address) as client:
                _LOGGER.info(f"Connected to BLE device {ble_device.address}")
                
                # Obtenir les services
                services = await client.get_services()
                
                # Chercher une caractéristique d'écriture
                write_char = None
                for service in services.services:
                    for char in service.characteristics:
                        if "write" in char.properties:
                            write_char = char
                            break
                    if write_char:
                        break
                
                if not write_char:
                    _LOGGER.error("No writable characteristic found")
                    return False
                
                # Protocole simple : [on_byte, brightness_byte]
                pwm_byte = min(255, brightness_pct * 255 // 100)
                on_byte = 0x01 if on else 0x00
                data = bytes([on_byte, pwm_byte])
                
                await client.write_gatt_char(write_char.uuid, data)
                _LOGGER.info(f"BLE command sent: on={on}, brightness={brightness_pct}%")
                
                return True
                
        except Exception as e:
            _LOGGER.error(f"Simple BLE control failed: {e}")
            return False
