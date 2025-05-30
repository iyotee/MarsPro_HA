from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
import voluptuous as vol
from .const import DOMAIN
import logging

_LOGGER = logging.getLogger(__name__)


class MarsHydroConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Mars Hydro."""

    VERSION = 1

    def __init__(self):
        self._email = None
        self._password = None
        self._api_type = None

    async def async_step_user(self, user_input=None) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            self._email = user_input["email"]
            self._password = user_input["password"]
            self._api_type = user_input.get("api_type", "marshydro")

            if not self._validate_email(self._email):
                errors["email"] = "invalid_email"
            else:
                login_success = await self._test_login(self._email, self._password, self._api_type)
                if login_success:
                    return self.async_create_entry(
                        title=f"Mars {'Pro' if self._api_type == 'marspro' else 'Hydro'}",
                        data={
                            "email": self._email, 
                            "password": self._password,
                            "api_type": self._api_type
                        },
                    )
                else:
                    errors["base"] = "cannot_connect"

        # Schema für das Eingabeformular avec choix du type d'API
        data_schema = vol.Schema(
            {
                vol.Required("email"): str,
                vol.Required("password"): str,
                vol.Required("api_type", default="marspro"): vol.In({
                    "marspro": "MarsPro (Nouvelle application)",
                    "marshydro": "MarsHydro (Ancienne application)"
                }),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )

    async def _test_login(self, email: str, password: str, api_type: str = "marshydro") -> bool:
        """Test the API login."""
        if api_type == "marspro":
            from .api_marspro import MarsProAPI
            api = MarsProAPI(email, password)
        else:
            from .api import MarsHydroAPI
            api = MarsHydroAPI(email, password)
        
        try:
            await api.login()
            return True
        except Exception as e:
            _LOGGER.error("Error testing login credentials for %s API: %s", api_type, e)
            return False

    @staticmethod
    def _validate_email(email: str) -> bool:
        """Validate an email address."""
        import re

        email_regex = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        return re.match(email_regex, email) is not None

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry):
        """Get the options flow."""
        return MarsHydroOptionsFlow(config_entry)


class MarsHydroOptionsFlow(config_entries.OptionsFlow):
    """Handle an options flow for Mars Hydro."""

    def __init__(self, config_entry: config_entries.ConfigEntry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None) -> FlowResult:
        """Handle the options flow."""
        errors = {}

        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        options_schema = vol.Schema(
            {
                vol.Required("update_interval", default=30): int,
                vol.Required("api_type", default=self.config_entry.data.get("api_type", "marspro")): vol.In({
                    "marspro": "MarsPro (Nouvelle application)",
                    "marshydro": "MarsHydro (Ancienne application)"
                }),
            }
        )

        return self.async_show_form(
            step_id="init",
            data_schema=options_schema,
            errors=errors,
        )
