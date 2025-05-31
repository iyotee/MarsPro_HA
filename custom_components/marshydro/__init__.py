from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers import device_registry as dr
from .const import DOMAIN
import logging

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor", "light", "switch", "fan"]  # Sensor hinzugefügt


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Setup für die Mars Hydro-Integration."""
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Mars Hydro integration from a config entry."""
    email = entry.data["email"]
    password = entry.data["password"]
    api_type = entry.data.get("api_type", "marshydro")  # Default à l'ancienne API pour la compatibilité

    # Créer l'instance API appropriée selon le type choisi
    if api_type == "marspro":
        from .api_marspro import MarsProAPI
        api = MarsProAPI(email, password)
        manufacturer = "Mars Pro"
        model_prefix = "MarsPro"
        _LOGGER.info("Utilisation de l'API MarsPro")
    else:
        from .api import MarsHydroAPI
        api = MarsHydroAPI(email, password)
        manufacturer = "Mars Hydro"
        model_prefix = "Mars Hydro"
        _LOGGER.info("Utilisation de l'API MarsHydro (legacy)")

    await api.login()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "api": api,
        "api_type": api_type,
        "manufacturer": manufacturer
    }

    # Gerät registrieren
    device_registry = dr.async_get(hass)

    # Récupérer les données de l'appareil principal
    device_data = await api.get_lightdata()
    if device_data:
        # Utiliser le PID stable comme identifiant au lieu de l'ID changeant
        stable_pid = device_data.get("device_pid_stable") or device_data.get("deviceSerialnum") or str(device_data.get("id"))
        device_name = device_data.get("deviceName", "Mars Device")
        
        # Déterminer le type d'appareil basé sur le nom
        device_name_lower = device_name.lower()
        if "dimbox" in device_name_lower or "light" in device_name_lower:
            device_type = "Light"
            _LOGGER.info(f"Device detected as LIGHT: {device_name}")
        elif "fan" in device_name_lower or "wind" in device_name_lower:
            device_type = "Fan" 
            _LOGGER.info(f"Device detected as FAN: {device_name}")
        else:
            device_type = "Light"  # Default to Light for DIMBOX devices
            _LOGGER.info(f"Device defaulted to LIGHT: {device_name}")
        
        # Enregistrer UN SEUL appareil avec l'identifiant stable
        device_registry.async_get_or_create(
            config_entry_id=entry.entry_id,
            identifiers={(DOMAIN, stable_pid)},  # Utiliser PID stable !
            manufacturer=manufacturer,
            name=device_name,
            model=f"{model_prefix} {device_type}",
        )
        _LOGGER.info(f"Device {device_name} registered with stable PID: {stable_pid}")
        
        # Stocker les informations pour les entités
        hass.data[DOMAIN][entry.entry_id]["device_type"] = device_type.lower()
        hass.data[DOMAIN][entry.entry_id]["stable_pid"] = stable_pid
        
    else:
        _LOGGER.warning("No device found, registration skipped.")

    # Plattformen laden
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Entferne eine Konfigurationsinstanz."""
    _LOGGER.debug("Mars Hydro async_unload_entry wird aufgerufen")

    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def create_api_instance(hass: HomeAssistant, email: str, password: str, api_type: str = "marshydro"):
    """Erstelle eine API-Instanz und führe den Login durch."""
    try:
        if api_type == "marspro":
            from .api_marspro import MarsProAPI
            api_instance = MarsProAPI(email, password)
        else:
            from .api import MarsHydroAPI
            api_instance = MarsHydroAPI(email, password)
            
        await api_instance.login()
        return api_instance
    except Exception as e:
        _LOGGER.error(f"Fehler beim Erstellen der API-Instanz ({api_type}): {e}")
        return None
