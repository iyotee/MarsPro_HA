# Intégration Mars Hydro/MarsPro pour Home Assistant

Cette intégration Home Assistant prend en charge les appareils Mars Hydro et MarsPro via le cloud.

## 🆕 Nouveautés - Support MarsPro

Cette version modifiée ajoute le support pour la **nouvelle application MarsPro** en plus de l'ancienne application MarsHydro.

### Fonctionnalités

- ✅ **Support dual** : MarsHydro (ancienne app) et MarsPro (nouvelle app)
- ✅ **Fallback automatique** : Si MarsPro échoue, retour automatique vers l'API MarsHydro
- ✅ **Configuration intuitive** : Choix du type d'API lors de la configuration
- ✅ **Compatibilité** : Fonctionne avec les configurations existantes

## 📱 Applications supportées

### MarsPro (Nouvelle application - Recommandée)
- Application moderne de Mars Hydro
- Interface utilisateur améliorée
- Nouvelles fonctionnalités

### MarsHydro (Ancienne application - Legacy)
- Application historique
- Conservée pour la compatibilité
- ⚠️ Peut déconnecter l'application mobile

## 🔧 Installation

1. **Installer via HACS** (recommandé)
   ```
   - Aller dans HACS > Intégrations
   - Cliquer sur les trois points > Dépôts personnalisés
   - Ajouter : https://github.com/iyotee/MarsPro_HA
   - Catégorie : Intégration
   - Installer "Mars Hydro"
   ```

2. **Installation manuelle**
   ```bash
   # Copier dans custom_components/marshydro/
   cp -r custom_components/marshydro /config/custom_components/
   ```

3. **Redémarrer Home Assistant**

## ⚙️ Configuration

1. **Aller dans Paramètres > Appareils et services**
2. **Cliquer sur "Ajouter une intégration"**
3. **Rechercher "Mars Hydro"**
4. **Remplir le formulaire :**
   - **Email** : Votre email Mars Hydro/MarsPro
   - **Mot de passe** : Votre mot de passe
   - **Type d'API** : 
     - `MarsPro (Nouvelle application)` - **Recommandé**
     - `MarsHydro (Ancienne application)` - Pour compatibilité

## 🔍 Différences techniques

### Endpoints API

**MarsPro (Hypothétiques - à ajuster selon les découvertes)**
```
Base URL: https://api.marspro.com/api
- /auth/login - Authentification
- /device/list - Liste des appareils
- /device/control - Contrôle on/off
- /device/setBrightness - Luminosité
- /device/setFanSpeed - Vitesse ventilateur
```

**MarsHydro (Existant)**
```
Base URL: https://api.lgledsolutions.com/api/android
- /ulogin/mailLogin/v1 - Authentification
- /udm/getDeviceList/v1 - Liste des appareils
- /udm/lampSwitch/v1 - Contrôle on/off
- /udm/adjustLight/v1 - Luminosité/vitesse
```

## 🐛 Dépannage

### L'API MarsPro ne fonctionne pas
```log
ERROR: MarsPro login failed: ...
INFO: Attempting fallback to legacy MarsHydro API...
INFO: Fallback to legacy API successful
```
➡️ **Solution** : L'intégration utilise automatiquement l'ancienne API

### Pas d'appareils trouvés
1. Vérifier que les appareils sont connectés dans l'app mobile
2. Essayer l'autre type d'API
3. Vérifier les logs Home Assistant

### Déconnexion de l'app mobile
⚠️ **Normal avec l'API MarsHydro** - Un seul appareil peut être connecté à la fois

## 📋 Logs de débogage

Pour activer les logs détaillés, ajouter dans `configuration.yaml` :

```yaml
logger:
  default: warning
  logs:
    custom_components.marshydro: debug
```

## 🚀 Prochaines étapes

1. **Tests avec MarsPro** : Identifier les vrais endpoints
2. **Capture de trafic** : Analyser les requêtes de l'app MarsPro
3. **Ajustements API** : Adapter selon les découvertes
4. **Tests utilisateurs** : Validation avec de vrais comptes MarsPro

## 🤝 Contribution

Vous pouvez aider en :
- **Testant** l'intégration avec MarsPro
- **Partageant** les logs d'erreur
- **Analysant** le trafic réseau de l'app MarsPro
- **Reportant** les bugs

## 📄 Licence

MIT License - Voir fichier LICENSE

## 🙏 Crédits

- **Projet original** : [suppqt/hass_mars_hydro](https://github.com/suppqt/hass_mars_hydro)
- **Fork initial** : [iyotee/MarsPro_HA](https://github.com/iyotee/MarsPro_HA)
- **Adaptation MarsPro** : Cette version 