from homeassistant.components.light import LightEntity, ATTR_BRIGHTNESS
from . import _LOGGER, DOMAIN


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the Mars Hydro Light entity."""
    _LOGGER.debug("Mars Hydro Light async_setup_entry called")

    api = hass.data[DOMAIN][entry.entry_id].get("api")

    if api:
        light = MarsHydroBrightnessLight(api, entry.entry_id)
        async_add_entities([light], update_before_add=True)


class MarsHydroBrightnessLight(LightEntity):
    """Representation of the Mars Hydro Light with brightness control only."""

    def __init__(self, api, entry_id):
        self._api = api
        self._device_id = None  # To store the dynamic device_id (for logging)
        self._stable_pid = None  # To store the stable PID (for identifiers)
        self._device_name = None  # To store the dynamic deviceName
        self._brightness = None
        self._available = False
        self._state = None
        self._entry_id = entry_id

    @property
    def name(self):
        """Return the name of the light, dynamically including the device name."""
        if self._device_name:
            return self._device_name
        return "Mars Hydro Brightness Light"

    @property
    def brightness(self):
        """Return the brightness of the light (0-255)."""
        return self._brightness

    @property
    def available(self):
        """Return True if entity is available."""
        return self._available

    @property
    def is_on(self):
        """Return True if the light is on."""
        return self._state

    @property
    def unique_id(self):
        """Return a unique ID for the light using stable PID."""
        return (
            f"{self._entry_id}_light_{self._stable_pid}"
            if self._stable_pid
            else f"{self._entry_id}_light"
        )

    @property
    def device_info(self):
        """Return device information for linking with the device registry."""
        if not self._stable_pid or not self._device_name:
            return None

        return {
            "identifiers": {
                (DOMAIN, self._stable_pid)  # Use stable PID for device linking
            },
            "name": self._device_name,
            "manufacturer": "Mars Hydro",
            "model": "Mars Hydro Light",
        }

    @property
    def supported_color_modes(self):
        """Return the list of supported color modes."""
        return {"brightness"}

    @property
    def color_mode(self):
        """Return the current color mode."""
        return "brightness"

    async def async_turn_on(self, **kwargs):
        """Turn on the light by setting the brightness."""
        brightness = kwargs.get(ATTR_BRIGHTNESS, 255)  # Default to max brightness
        await self.async_set_brightness(brightness)
        self._state = True

    async def async_turn_off(self, **kwargs):
        """Turn off the light by setting brightness to 0."""
        await self.async_set_brightness(0)
        self._state = False

    async def async_set_brightness(self, brightness: int):
        """Set the brightness of the light using hybrid control (BLE/Cloud)."""
        try:
            brightness_percentage = round((brightness / 255) * 100)
            is_on = brightness > 0
            
            _LOGGER.info(f"Setting brightness to {brightness_percentage}% (on={is_on})")
            
            # Utiliser la méthode hybride qui détecte automatiquement Bluetooth vs WiFi
            success = await self._api.safe_api_call(
                self._api.control_device_hybrid, is_on, brightness_percentage
            )
            
            if success:
                self._brightness = brightness
                self._state = is_on
                self._available = True
                _LOGGER.info(f"Hybrid control successful: {brightness_percentage}% (Bluetooth/WiFi)")
            else:
                # Fallback vers l'ancienne méthode set_brightness
                _LOGGER.warning("Hybrid control failed, trying legacy method...")
                response = await self._api.safe_api_call(
                    self._api.set_brightness, brightness_percentage
                )
                
                if response and response.get("code") == "102":
                    _LOGGER.warning("Token expired, re-authenticating...")
                    await self._api.login()
                    response = await self._api.safe_api_call(
                        self._api.set_brightness, brightness_percentage
                    )

                if response and response.get("code") == "000":
                    self._brightness = brightness
                    self._state = is_on
                    self._available = True
                    _LOGGER.info(f"Legacy control successful: {brightness_percentage}%")
                else:
                    error_msg = response.get('msg') if response else 'No response'
                    raise Exception(f"All control methods failed: {error_msg}")
                    
        except Exception as e:
            self._available = False
            _LOGGER.error(f"Error setting brightness: {e}")
            # Ne pas lever l'exception pour éviter de casser l'entité

    async def async_update(self):
        """Update the light's state."""
        try:
            light_data = await self._api.safe_api_call(self._api.get_lightdata)
            if light_data:
                # Récupérer l'ID pour le logging et le PID stable pour les identifiants
                self._device_id = light_data.get("id")  # For logging only
                self._stable_pid = (light_data.get("device_pid_stable") or 
                                  light_data.get("deviceSerialnum") or 
                                  str(light_data.get("id", "")))  # Stable identifier
                self._device_name = light_data.get("deviceName")
                
                # Gérer deviceLightRate qui peut être -1
                light_rate = light_data.get("deviceLightRate", 0)
                if light_rate == -1:
                    # Si deviceLightRate est -1, utiliser une valeur par défaut basée sur isClose
                    if light_data.get("isClose", False):
                        self._brightness = 0  # Device is OFF
                        self._state = False
                    else:
                        self._brightness = 255  # Device is ON, assume full brightness
                        self._state = True
                else:
                    # Utiliser la valeur normale
                    self._brightness = int((light_rate / 100) * 255)
                    self._state = not light_data.get("isClose", False)
                
                self._available = True
                _LOGGER.info(f"Updated light: {self._device_name} (PID: {self._stable_pid}), brightness: {self._brightness}, state: {self._state}")
            else:
                self._available = False
                self._state = None
                _LOGGER.warning("Couldn't retrieve light data")
        except Exception as e:
            self._available = False
            self._state = None
            _LOGGER.error(f"Error updating light state: {e}")
