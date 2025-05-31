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

    # Attendre que le coordinateur ait des données
    if not coordinator.data:
        _LOGGER.warning("No coordinator data available")
        return

    devices = coordinator.data.get("devices", [])
    light_devices = [device for device in devices if device['entity_type'] == 'light']
    
    _LOGGER.info(f"Setting up {len(light_devices)} light entities")

    # Créer une entité pour chaque appareil light détecté
    for device in light_devices:
        device_id = device['id']
        device_name = device['name']
        device_pid = device['pid']
        is_bluetooth = device['is_bluetooth']
        
        # Entité cloud (toujours créée)
        cloud_entity = MarsHydroCloudLight(
            coordinator, api, config_entry, device_id, device_name, device_pid
        )
        entities.append(cloud_entity)
        _LOGGER.info(f"Created cloud light entity: {device_name} (ID: {device_id})")
        
        # Entité BLE (si appareil Bluetooth)
        if is_bluetooth:
            ble_entity = MarsHydroBluetoothLight(
                coordinator, api, config_entry, device_id, device_name, device_pid
            )
            entities.append(ble_entity)
            _LOGGER.info(f"Created BLE light entity: {device_name} (ID: {device_id})")

    if entities:
        async_add_entities(entities, update_before_add=True)
        _LOGGER.info(f"Added {len(entities)} light entities to Home Assistant")
    else:
        _LOGGER.warning("No light entities to add")


class MarsHydroCloudLight(CoordinatorEntity, LightEntity):
    """Entité light MarsHydro (contrôle cloud/WiFi)."""

    _attr_color_mode = ColorMode.BRIGHTNESS
    _attr_supported_color_modes = {ColorMode.BRIGHTNESS}
    _attr_supported_features = LightEntityFeature.TRANSITION

    def __init__(self, coordinator, api, config_entry, device_id, device_name, device_pid):
        """Initialize the cloud light."""
        super().__init__(coordinator)
        self.api = api
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
        """Instruct the light to turn on."""
        brightness = kwargs.get(ATTR_BRIGHTNESS)
        
        if brightness is not None:
            # Convertir de HA (0-255) vers pourcentage (0-100)
            brightness_pct = int(brightness * 100 / 255)
        else:
            brightness_pct = 100

        _LOGGER.info(f"Turning on cloud light {self._device_name} with brightness {brightness_pct}%")
        
        try:
            # Utiliser la méthode control_device_by_pid
            success = await self.api.control_device_by_pid(self._device_pid, True, brightness_pct)
            
            if success:
                self._is_on = True
                self._brightness = brightness if brightness is not None else 255
                self.async_write_ha_state()
                _LOGGER.info(f"Successfully turned on cloud light {self._device_name}")
            else:
                _LOGGER.error(f"Failed to turn on cloud light {self._device_name}")
                
        except Exception as e:
            _LOGGER.error(f"Error turning on cloud light {self._device_name}: {e}")

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Instruct the light to turn off."""
        _LOGGER.info(f"Turning off cloud light {self._device_name}")
        
        try:
            # Utiliser control_device_by_pid avec PWM 0
            success = await self.api.control_device_by_pid(self._device_pid, False, 0)
            
            if success:
                self._is_on = False
                self._brightness = 0
                self.async_write_ha_state()
                _LOGGER.info(f"Successfully turned off cloud light {self._device_name}")
            else:
                _LOGGER.error(f"Failed to turn off cloud light {self._device_name}")
                
        except Exception as e:
            _LOGGER.error(f"Error turning off cloud light {self._device_name}: {e}")


class MarsHydroBluetoothLight(CoordinatorEntity, LightEntity):
    """Entité light MarsHydro Bluetooth BLE directe."""

    _attr_color_mode = ColorMode.BRIGHTNESS
    _attr_supported_color_modes = {ColorMode.BRIGHTNESS}
    _attr_supported_features = LightEntityFeature.TRANSITION

    def __init__(self, coordinator, api, config_entry, device_id, device_name, device_pid):
        """Initialize the Bluetooth light."""
        super().__init__(coordinator)
        self.api = api
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
        return f"{self._device_name} (BLE)"

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
        # L'entité BLE est disponible si le scan Bluetooth a trouvé des appareils
        return len(self.coordinator.bluetooth_devices) > 0

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Instruct the light to turn on via Bluetooth BLE."""
        brightness = kwargs.get(ATTR_BRIGHTNESS, 255)
        brightness_pct = int(brightness * 100 / 255)
        
        _LOGGER.info(f"Turning on BLE light {self._device_name} with brightness {brightness_pct}%")
        
        try:
            # Essayer de contrôler via BLE (si méthode disponible)
            if hasattr(self.api, 'control_device_ble'):
                success = await self.api.control_device_ble(self._device_pid, True, brightness_pct)
            else:
                # Fallback vers contrôle cloud
                success = await self.api.control_device_by_pid(self._device_pid, True, brightness_pct)
            
            if success:
                self._is_on = True
                self._brightness = brightness
                self.async_write_ha_state()
                _LOGGER.info(f"Successfully turned on BLE light {self._device_name}")
            else:
                _LOGGER.error(f"Failed to turn on BLE light {self._device_name}")
                
        except Exception as e:
            _LOGGER.error(f"Error turning on BLE light {self._device_name}: {e}")

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Instruct the light to turn off via Bluetooth BLE."""
        _LOGGER.info(f"Turning off BLE light {self._device_name}")
        
        try:
            # Essayer de contrôler via BLE (si méthode disponible)
            if hasattr(self.api, 'control_device_ble'):
                success = await self.api.control_device_ble(self._device_pid, False, 0)
            else:
                # Fallback vers contrôle cloud
                success = await self.api.control_device_by_pid(self._device_pid, False, 0)
            
            if success:
                self._is_on = False
                self._brightness = 0
                self.async_write_ha_state()
                _LOGGER.info(f"Successfully turned off BLE light {self._device_name}")
            else:
                _LOGGER.error(f"Failed to turn off BLE light {self._device_name}")
                
        except Exception as e:
            _LOGGER.error(f"Error turning off BLE light {self._device_name}: {e}")
