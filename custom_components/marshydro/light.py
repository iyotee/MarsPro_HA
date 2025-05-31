"""Support for MarsHydro lights avec modèle hybride Cloud + BLE."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.light import ATTR_BRIGHTNESS, ColorMode, LightEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up MarsHydro lights from a config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    
    # Attendre que le coordinateur récupère les données
    await coordinator.async_config_entry_first_refresh()
    
    lights = []
    
    # Créer entités pour les appareils de type "light"
    light_devices = coordinator.get_devices_by_type("light")
    
    for device in light_devices:
        device_id = device['id']
        device_name = device['name']
        device_pid = device['pid']
        is_bluetooth = device.get('is_bluetooth', False)
        
        _LOGGER.info(f"Creating light entity for {device_name} (ID: {device_id}, PID: {device_pid})")
        
        if is_bluetooth:
            # Appareil hybride: Cloud + BLE requis
            _LOGGER.info(f"Device {device_name} uses HYBRID model (Cloud API + BLE)")
            light_entity = MarsHydroHybridLight(coordinator, device)
        else:
            # Appareil cloud seul
            _LOGGER.info(f"Device {device_name} uses Cloud-only model")
            light_entity = MarsHydroCloudLight(coordinator, device)
        
        lights.append(light_entity)
    
    if lights:
        _LOGGER.info(f"Adding {len(lights)} MarsHydro light entities")
        async_add_entities(lights)
    else:
        _LOGGER.warning("No light devices found to add")


class MarsHydroBaseLight(CoordinatorEntity, LightEntity):
    """Base class for MarsHydro lights."""
    
    def __init__(self, coordinator, device):
        """Initialize the light."""
        super().__init__(coordinator)
        self.device = device
        self.device_id = device['id']
        self.device_name = device['name']
        self.device_pid = device['pid']
        
        # Identifiants uniques pour Home Assistant
        self._attr_unique_id = f"marspro_{self.device_id}"
        self._attr_name = f"MarsPro {self.device_id}"
        
        # Configuration couleur
        self._attr_color_mode = ColorMode.BRIGHTNESS
        self._attr_supported_color_modes = {ColorMode.BRIGHTNESS}
        
        # État par défaut
        self._attr_brightness = 128
        self._attr_is_on = False
        
        _LOGGER.info(f"Initialized {self.__class__.__name__}: {self._attr_name}")

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        return DeviceInfo(
            identifiers={(DOMAIN, str(self.device_id))},
            name=self.device_name,
            manufacturer="MarsHydro",
            model="MarsHydro Light",
            sw_version="2.3.0-final",
        )

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return entity specific state attributes."""
        attributes = {
            "device_id": self.device_id,
            "pid": self.device_pid,
            "device_name": self.device_name,
            "integration_version": "2.3.0-final",
        }
        return attributes


class MarsHydroCloudLight(MarsHydroBaseLight):
    """MarsHydro light avec contrôle Cloud uniquement."""
    
    def __init__(self, coordinator, device):
        super().__init__(coordinator, device)
        self.control_mode = "cloud_only"
    
    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return entity specific state attributes."""
        attributes = super().extra_state_attributes
        attributes.update({
            "control_mode": self.control_mode,
        })
        return attributes

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the light."""
        try:
            brightness = kwargs.get(ATTR_BRIGHTNESS, 255)
            brightness_percent = int((brightness / 255) * 100)
            
            _LOGGER.info(f"Turning ON {self.device_name} with brightness {brightness_percent}% (Cloud)")
            
            # Contrôle via Cloud API
            success = await self.coordinator.api.turn_on_device(
                self.device_id, brightness_percent
            )
            
            if success:
                self._attr_is_on = True
                self._attr_brightness = brightness
                _LOGGER.info(f"✅ Successfully turned ON {self.device_name}")
            else:
                _LOGGER.error(f"❌ Failed to turn ON {self.device_name}")
            
            self.async_write_ha_state()
            
        except Exception as e:
            _LOGGER.error(f"Error turning on {self.device_name}: {e}")

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the light."""
        try:
            _LOGGER.info(f"Turning OFF {self.device_name} (Cloud)")
            
            success = await self.coordinator.api.turn_off_device(self.device_id)
            
            if success:
                self._attr_is_on = False
                _LOGGER.info(f"✅ Successfully turned OFF {self.device_name}")
            else:
                _LOGGER.error(f"❌ Failed to turn OFF {self.device_name}")
            
            self.async_write_ha_state()
            
        except Exception as e:
            _LOGGER.error(f"Error turning off {self.device_name}: {e}")


class MarsHydroHybridLight(MarsHydroBaseLight):
    """MarsHydro light avec modèle hybride Cloud + BLE (LOGIQUE AMÉLIORÉE)."""
    
    def __init__(self, coordinator, device):
        super().__init__(coordinator, device)
        self.control_mode = "hybrid_ble_cloud"
        self.ble_connected = False
        self.last_ble_attempt = None
        self.ble_connection_retries = 0
        self.max_ble_retries = 3
    
    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return entity specific state attributes."""
        attributes = super().extra_state_attributes
        attributes.update({
            "control_mode": self.control_mode,
            "ble_connected": self.ble_connected,
            "ble_retries": self.ble_connection_retries,
        })
        return attributes

    async def _ensure_ble_connection(self) -> bool:
        """S'assurer qu'on a une connexion BLE (LOGIQUE AMÉLIORÉE)."""
        try:
            # Vérifier si on a déjà épuisé les tentatives
            if self.ble_connection_retries >= self.max_ble_retries:
                _LOGGER.warning(f"Max BLE retries reached for {self.device_name}, using cloud-only fallback")
                return False
            
            # Tenter d'établir la connexion BLE
            client = await self.coordinator.establish_ble_connection(self.device_pid)
            
            if client:
                self.ble_connected = True
                self.ble_connection_retries = 0  # Reset sur succès
                _LOGGER.info(f"✅ BLE connection ready for {self.device_name}")
                return True
            else:
                self.ble_connected = False
                self.ble_connection_retries += 1
                _LOGGER.warning(f"❌ BLE connection failed for {self.device_name} (attempt {self.ble_connection_retries}/{self.max_ble_retries})")
                
                # Si plus de tentatives possibles, passer en mode cloud-only temporaire
                if self.ble_connection_retries >= self.max_ble_retries:
                    _LOGGER.warning(f"Switching {self.device_name} to cloud-only mode after {self.max_ble_retries} failed BLE attempts")
                    self.control_mode = "cloud_fallback"
                
                return False
                
        except Exception as e:
            self.ble_connected = False
            self.ble_connection_retries += 1
            _LOGGER.error(f"BLE connection error for {self.device_name}: {e}")
            return False

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the light avec modèle hybride AMÉLIORÉ."""
        try:
            brightness = kwargs.get(ATTR_BRIGHTNESS, 255)
            brightness_percent = int((brightness / 255) * 100)
            
            _LOGGER.info(f"Turning ON {self.device_name} with brightness {brightness_percent}% (Hybrid mode)")
            
            # ÉTAPE 1: Tenter connexion BLE si pas encore en fallback
            if self.control_mode != "cloud_fallback":
                ble_ready = await self._ensure_ble_connection()
                if not ble_ready:
                    _LOGGER.warning(f"BLE not available for {self.device_name}, using cloud-only")
            else:
                _LOGGER.info(f"Using cloud-only fallback for {self.device_name}")
                ble_ready = False
            
            # ÉTAPE 2: Envoyer commande cloud (toujours nécessaire même avec BLE)
            success = await self.coordinator.api.turn_on_device(
                self.device_id, brightness_percent
            )
            
            if success:
                self._attr_is_on = True
                self._attr_brightness = brightness
                
                if self.ble_connected:
                    _LOGGER.info(f"✅ Successfully turned ON {self.device_name} (Hybrid: Cloud + BLE)")
                else:
                    _LOGGER.info(f"✅ Successfully turned ON {self.device_name} (Cloud fallback)")
            else:
                _LOGGER.error(f"❌ Failed to turn ON {self.device_name} (Cloud command failed)")
            
            self.async_write_ha_state()
            
        except Exception as e:
            _LOGGER.error(f"Error turning on {self.device_name}: {e}")

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the light avec modèle hybride AMÉLIORÉ."""
        try:
            _LOGGER.info(f"Turning OFF {self.device_name} (Hybrid mode)")
            
            # ÉTAPE 1: Tenter connexion BLE si pas encore en fallback
            if self.control_mode != "cloud_fallback":
                ble_ready = await self._ensure_ble_connection()
                if not ble_ready:
                    _LOGGER.warning(f"BLE not available for {self.device_name}, using cloud-only")
            else:
                _LOGGER.info(f"Using cloud-only fallback for {self.device_name}")
            
            # ÉTAPE 2: Envoyer commande cloud
            success = await self.coordinator.api.turn_off_device(self.device_id)
            
            if success:
                self._attr_is_on = False
                
                if self.ble_connected:
                    _LOGGER.info(f"✅ Successfully turned OFF {self.device_name} (Hybrid: Cloud + BLE)")
                else:
                    _LOGGER.info(f"✅ Successfully turned OFF {self.device_name} (Cloud fallback)")
            else:
                _LOGGER.error(f"❌ Failed to turn OFF {self.device_name} (Cloud command failed)")
            
            self.async_write_ha_state()
            
        except Exception as e:
            _LOGGER.error(f"Error turning off {self.device_name}: {e}")

    async def async_update(self) -> None:
        """Update the light state. Essayer de reconnecter BLE périodiquement."""
        await super().async_update()
        
        # Essayer de reconnecter BLE toutes les 5 minutes si en fallback
        if (self.control_mode == "cloud_fallback" and 
            self.ble_connection_retries < self.max_ble_retries):
            
            # Reset des tentatives après un certain temps
            import time
            current_time = time.time()
            if (self.last_ble_attempt is None or 
                current_time - self.last_ble_attempt > 300):  # 5 minutes
                
                _LOGGER.info(f"Attempting to restore BLE for {self.device_name}")
                self.ble_connection_retries = 0
                self.control_mode = "hybrid_ble_cloud"
                self.last_ble_attempt = current_time
