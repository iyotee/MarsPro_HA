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

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            mode = user_input.get("mode")
            
            if mode == "cloud":
                return await self.async_step_cloud(user_input)
            elif mode == "ble_pure":
                return await self.async_step_ble_pure(user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("mode", default="cloud"): vol.In({
                    "cloud": "Mode Hybride (Cloud + BLE)",
                    "ble_pure": "Mode BLE Pur (Bluetooth uniquement)"
                })
            }),
            errors=errors,
        )

    async def async_step_cloud(self, user_input=None):
        """Handle cloud configuration step."""
        errors = {}

        if user_input is not None:
            email = user_input["email"]
            password = user_input["password"]

            # Test login
            api = MarsProAPI(email, password)
            try:
                login_success = await api.login()
                if login_success:
                    return self.async_create_entry(
                        title="MarsHydro (Cloud + BLE)",
                        data={
                            "mode": "cloud",
                            "email": email,
                            "password": password,
                        },
                    )
                else:
                    errors["base"] = "invalid_auth"
            except Exception:
                errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="cloud",
            data_schema=vol.Schema({
                vol.Required("email"): str,
                vol.Required("password"): str,
            }),
            errors=errors,
        )

    async def async_step_ble_pure(self, user_input=None):
        """Handle BLE pure configuration step."""
        errors = {}

        if user_input is not None:
            # Scanner les appareils BLE MarsPro
            try:
                from bleak import BleakScanner
                
                _LOGGER.info("Scanning for MarsPro BLE devices...")
                devices = await BleakScanner.discover(timeout=10.0)
                
                marspro_devices = []
                for device in devices:
                    if self._is_marspro_ble_device(device):
                        # Extraire PID depuis manufacturer_data
                        pid = self._extract_pid_from_ble(device)
                        marspro_devices.append({
                            'name': device.name,
                            'address': device.address,
                            'pid': pid,
                            'rssi': getattr(device, 'rssi', -50)
                        })
                
                if marspro_devices:
                    _LOGGER.info(f"Found {len(marspro_devices)} MarsPro BLE devices")
                    return self.async_create_entry(
                        title="MarsHydro (BLE Pur)",
                        data={
                            "mode": "ble_pure",
                            "ble_devices": marspro_devices,
                        },
                    )
                else:
                    errors["base"] = "no_ble_devices"
                    
            except ImportError:
                errors["base"] = "bleak_not_available"
            except Exception as e:
                _LOGGER.error(f"BLE scan error: {e}")
                errors["base"] = "ble_scan_failed"

        return self.async_show_form(
            step_id="ble_pure",
            data_schema=vol.Schema({}),
            errors=errors,
            description_placeholders={
                "info": "Cette option scanne et configure les appareils MarsPro via Bluetooth uniquement, sans connexion cloud."
            }
        )

    def _is_marspro_ble_device(self, device) -> bool:
        """Vérifier si un appareil BLE est MarsPro."""
        device_name = (device.name or "").lower()
        
        # Patterns MarsPro
        if any(pattern in device_name for pattern in ["mh-dimbox", "mars", "dimbox"]):
            return True
            
        # Vérifier manufacturer_data pour pattern MarsPro
        if hasattr(device, 'metadata') and device.metadata:
            manufacturer_data = device.metadata.get('manufacturer_data', {})
            for key, value in manufacturer_data.items():
                if isinstance(value, (bytes, str)):
                    hex_data = value.hex() if isinstance(value, bytes) else value
                    # Chercher pattern PID MarsPro (12 hex chars)
                    if len(hex_data) >= 12 and any(
                        char in hex_data.lower() for char in ['345f45ec73cc', 'marspro']
                    ):
                        return True
        
        return False

    def _extract_pid_from_ble(self, device) -> str:
        """Extraire PID depuis les données BLE."""
        # Méthode 1: Depuis le nom
        if device.name:
            import re
            pid_match = re.search(r'([A-F0-9]{12})', device.name.upper())
            if pid_match:
                return pid_match.group(1)
        
        # Méthode 2: Depuis manufacturer_data
        if hasattr(device, 'metadata') and device.metadata:
            manufacturer_data = device.metadata.get('manufacturer_data', {})
            for key, value in manufacturer_data.items():
                if isinstance(value, bytes):
                    hex_data = value.hex()
                elif isinstance(value, str):
                    hex_data = value
                else:
                    continue
                    
                # Chercher pattern PID (12 caractères hex consécutifs)
                import re
                pid_matches = re.findall(r'([a-fA-F0-9]{12})', hex_data)
                if pid_matches:
                    return pid_matches[0].upper()
        
        # Méthode 3: Depuis l'adresse MAC (transformation)
        if device.address:
            # 34:5F:45:EC:73:CE → 345F45EC73CC (sans les derniers segments)
            mac_clean = device.address.replace(":", "").upper()
            if len(mac_clean) == 12:
                return mac_clean
        
        return "UNKNOWN"

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
