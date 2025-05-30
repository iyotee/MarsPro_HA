# Changelog

## [2.0.0] - 2025-01-XX - Support MarsPro

### 🆕 Nouveautés
- **Support MarsPro** : Ajout du support pour la nouvelle application MarsPro
- **API dual** : Choix entre MarsHydro (legacy) et MarsPro lors de la configuration
- **Fallback automatique** : Si MarsPro échoue, retour automatique vers l'API MarsHydro
- **Configuration améliorée** : Interface utilisateur avec sélection du type d'API
- **Outils de développement** : Scripts de découverte et test des APIs

### 🔧 Améliorations
- Refactorisation du code API pour supporter plusieurs backends
- Logs améliorés avec indication du type d'API utilisée
- Gestion d'erreur robuste avec fallback
- Documentation française complète

### 🛠️ Technique
- Nouvelle classe `MarsProAPI` avec endpoints hypothétiques
- Modification du `config_flow` pour le choix d'API
- Mise à jour du manifest (v2.0.0)
- Remplacement de `requests` par `aiohttp` pour de meilleures performances

### 📁 Nouveaux fichiers
- `custom_components/marshydro/api_marspro.py` - Nouvelle API MarsPro
- `tools/api_discovery.py` - Script de découverte d'endpoints
- `tools/test_integration.py` - Script de test
- `README_MarsPro.md` - Documentation française

### ⚠️ Notes importantes
- Les endpoints MarsPro sont hypothétiques et nécessitent des ajustements
- Le fallback vers MarsHydro assure la continuité de service
- Configuration existante compatible (défaut sur MarsHydro legacy)

### 🔮 Prochaines étapes
- Identification des vrais endpoints MarsPro
- Tests avec utilisateurs MarsPro
- Optimisation basée sur les retours

---

## [1.0.4] - 2024-XX-XX - Version originale

### Features
- Support for Mars Hydro lights and fans
- Cloud API integration
- Home Assistant entities for brightness, fan speed, temperature, humidity
- Switch controls for device power

### Known Issues
- ⚠️ API only supports one device to be logged in
- Only works with MarsHydro App, not MarsPro
- May disconnect mobile app when Home Assistant connects

## Version 1.0.3

- fixxed missing toggle_switch function

## Version 1.0.2

### 🚀 New Features

- **Fan Entity**
  - Added a fan entity with speed control via a slider (25%-100%).
  - Initial slider value uses `deviceLightRate` from `get_fandata`.
  - Included `async_turn_on`, `async_turn_off`, and detailed logging for improved control.

- **Fan Sensors**
  - Introduced new sensors to monitor:
    - **Temperature** (°F and °C).
    - **Humidity**.
    - **Fan speed**.
  - Handles invalid or missing data gracefully with enhanced logging.

### 🔧 API Updates

- Added a new `set_fanspeed` method, based on `set_brightness`, to control fan speed.
- Enhanced logging for all API calls, including detailed request and response data.

### 🖼️ Device Registry

- Integrated device images into Home Assistant using the `deviceImage` URL from `get_lightdata` and `get_fandata`.

### 🐛 Bug Fixes

- Fixed fan and light device ID mix-up issues.
- Ensured fan speed values are clamped to the valid range of 25%-100%.

### 📈 General Improvements

- Enhanced logging for debugging and monitoring.
- Improved dynamic handling of device names and IDs.
- Added robust error handling for a more seamless integration.

---

This release introduces fan support, expands sensor functionality, and significantly improves the integration's stability and usability.
