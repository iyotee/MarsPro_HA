"""Config flow for MarsHydro integration with Bluetooth support."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
from homeassistant.components import bluetooth

from .const import DOMAIN
from .api_marspro import MarsProAPI

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required("email"): str,
        vol.Required("password"): str,
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    email = data["email"]
    password = data["password"]

    # Test de connexion
    api = MarsProAPI(email, password)
    
    try:
        await api.login()
        
        # Vérifier si des appareils sont disponibles
        devices = await api.get_all_devices()
        
        # Détecter le support Bluetooth
        bluetooth_available = bluetooth.async_scanner_count(hass) > 0
        
        return {
            "title": f"MarsPro ({email})",
            "devices_found": len(devices),
            "bluetooth_available": bluetooth_available,
            "api": api,
        }
    except Exception as e:
        _LOGGER.error(f"Authentication failed: {e}")
        raise InvalidAuth from e


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for MarsHydro."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                # Check if already configured
                await self.async_set_unique_id(user_input["email"])
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=info["title"], 
                    data=user_input,
                    description_placeholders={
                        "devices_found": str(info["devices_found"]),
                        "bluetooth_status": "✅ Disponible" if info["bluetooth_available"] else "❌ Non disponible"
                    }
                )

        return self.async_show_form(
            step_id="user", 
            data_schema=STEP_USER_DATA_SCHEMA, 
            errors=errors,
            description_placeholders={
                "bluetooth_info": self._get_bluetooth_info()
            }
        )

    def _get_bluetooth_info(self) -> str:
        """Get Bluetooth availability info."""
        bluetooth_available = bluetooth.async_scanner_count(self.hass) > 0
        
        if bluetooth_available:
            return "🔵 Bluetooth BLE disponible - Support des appareils Bluetooth MarsPro activé"
        else:
            return "⚠️ Bluetooth BLE non disponible - Seuls les appareils WiFi/cloud seront supportés"


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
