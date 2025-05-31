# 📜 Changelog - MarsHydro Home Assistant Integration

## [2.3.0-FINAL] - 2025-01-27 🎯 DÉCOUVERTE MODÈLE HYBRIDE

### 🔍 RÉVÉLATION TECHNIQUE MAJEURE
**Découverte du modèle de fonctionnement hybride MarsPro :**
- 📱 App MarsPro ←→ 🌐 Cloud API ←→ 📡 Bluetooth BLE ←→ 💡 Appareil
- **Connexion BLE requise** + **Commandes via Cloud API**
- Pattern découvert : `MH-DIMBOX` (BLE) ↔ `345F45EC73CC` (PID)

### ✅ Nouveautés Majeures
- **MODÈLE HYBRIDE** : Support BLE + Cloud simultané pour MarsPro
- **Gestion BLE avancée** : Connexions persistantes avec `establish_ble_connection()`
- **Corrélation automatique** : BLE ↔ Cloud basée sur patterns découverts
- **Entités intelligentes** : Détection automatique du mode optimal (Hybride/Cloud/BLE)
- **Attributs diagnostics** : BLE RSSI, état connexion, mode contrôle
- **Documentation technique** : Reverse engineering complet du protocole

### 🔧 Améliorations Techniques
- **Coordinateur hybride** : `MarsHydroDataUpdateCoordinator` avec support BLE
- **Scanner BLE intelligent** : Détection patterns MarsPro (`mh-dimbox`, PIDs)
- **Gestion des connexions** : Pool de clients BLE avec cleanup automatique
- **Séquence d'activation** : addDevice → setDeviceActive → setBrightness
- **Modes de contrôle** : Hybride, Cloud seul, BLE direct expérimental

### 🐛 Corrections
- **Imports entités** : Correction `device.get('name')` vs `device.get('deviceName')`
- **Support is_net_device** : Détection correcte appareils Bluetooth
- **Noms d'entités** : Format unifié basé sur PIDs extraits
- **Gestion erreurs BLE** : Fallback gracieux si Bluetooth indisponible

### 📋 Entités Créées
```yaml
# Nouveau système d'entités basé sur le type détecté
light.mh_dimbox_345f45ec73cc          # HYBRIDE (BLE + Cloud)
light.marspro_wifi_device_cloud       # CLOUD seul
light.marspro_legacy_ble_direct       # BLE direct (expérimental)
```

### 🔬 Recherche et Documentation
- **Protocol MarsPro** : Documentation complète des endpoints
- **Patterns BLE** : Correspondance adresse MAC ↔ PID
- **Mode pairing** : Automatique lors déconnexion app officielle
- **Timing critique** : Délais optimaux pour synchronisation BLE ↔ Cloud

---

## [2.2.0] - 2025-01-25 🌐 API MARSPRO

### ✅ Ajouts
- **API MarsPro** : Intégration complète avec authentification
- **Détection automatique** : Scanner PIDs via getDeviceList
- **Support multi-appareils** : Gestion plusieurs lampes simultanément
- **Configuration UI** : Interface graphique pour credentials

### 🔧 Améliorations
- **Extraction PID** : Regex pour identifier appareils depuis noms
- **Types d'entités** : Détection automatique (light, fan, etc.)
- **Gestion erreurs** : Retry automatique et logs détaillés

---

## [2.1.0] - 2025-01-20 🔵 SUPPORT BLUETOOTH

### ✅ Ajouts
- **Bluetooth BLE** : Support via bleak
- **Scanner automatique** : Détection appareils Bluetooth
- **Entités duales** : Cloud + BLE pour chaque appareil
- **Configuration avancée** : Timeouts et paramètres BLE

### 🔧 Améliorations
- **Performance** : Scan BLE optimisé (10s timeout)
- **Fiabilité** : Détection patterns MarsPro améliorée
- **Logs** : Debug détaillé pour troubleshooting

---

## [2.0.0] - 2025-01-15 🏗️ REFACTORISATION MAJEURE

### ✅ Nouveautés
- **Architecture moderne** : Code Home Assistant 2025
- **Configuration UI** : Suppression configuration YAML
- **Support MarsPro** : Intégration app officielle
- **Multi-protocoles** : Cloud + Bluetooth simultané

### 💥 Breaking Changes
- **Configuration** : Migration vers UI (plus de YAML)
- **Noms entités** : Nouveau format basé sur PIDs
- **API** : Nouvelle classe MarsProAPI

### 🐛 Corrections
- **Stabilité** : Gestion reconnexions automatiques
- **Mémoire** : Nettoyage ressources améliore
- **Compatibilité** : Support HA 2024.1+

---

## [1.5.0] - 2024-12-10 🔧 AMÉLIORATIONS

### ✅ Ajouts
- **Transitions** : Support transitions lumières
- **Automations** : Exemples d'automations avancées
- **Scripts** : Templates pour séquences d'éclairage

### 🔧 Améliorations
- **Performance** : Optimisation requêtes API
- **UX** : Interface utilisateur améliorée
- **Documentation** : Guides d'installation détaillés

---

## [1.4.0] - 2024-11-20 📱 SUPPORT MARSHYDRO LEGACY

### ✅ Ajouts
- **Anciens modèles** : Support MarsHydro classiques
- **Rétrocompatibilité** : API legacy maintenue
- **Migration** : Outils de migration automatique

---

## [1.3.0] - 2024-11-01 ⚡ PERFORMANCE

### ✅ Ajouts
- **Cache intelligent** : Mise en cache des réponses API
- **Polling optimisé** : Réduction fréquence updates
- **Gestion d'état** : État local avec synchronisation cloud

### 🔧 Améliorations
- **Latence** : Réduction 50% temps de réponse
- **Ressources** : Utilisation CPU/mémoire optimisée
- **Stabilité** : Gestion déconnexions réseau

---

## [1.2.0] - 2024-10-15 🎛️ CONTRÔLES AVANCÉS

### ✅ Ajouts
- **Luminosité** : Contrôle 0-100% précis
- **Programmes** : Support cycles préprogrammés
- **Monitoring** : Température et humidité (si supporté)

---

## [1.1.0] - 2024-10-01 🔐 SÉCURITÉ

### ✅ Ajouts
- **Authentification sécurisée** : Tokens d'accès
- **Chiffrement** : Communications SSL/TLS
- **Validation** : Vérification certificats

### 🐛 Corrections
- **Authentification** : Correction expiration tokens
- **Reconnexion** : Gestion perte de connexion

---

## [1.0.0] - 2024-09-15 🎉 PREMIÈRE VERSION

### ✅ Fonctionnalités initiales
- **Intégration de base** : Support MarsPro cloud
- **Entités light** : Contrôle on/off et luminosité
- **Configuration** : Setup via configuration.yaml
- **API cloud** : Connexion serveurs MarsPro

### 📋 Composants
- `__init__.py` : Coordinateur principal
- `light.py` : Entités lumières
- `config_flow.py` : Configuration initiale
- `api_marspro.py` : Client API

---

## Légende des Icônes

- 🎯 **Découverte majeure** - Révélation technique importante
- ✅ **Nouveauté** - Nouvelle fonctionnalité
- 🔧 **Amélioration** - Enhancement existant
- 🐛 **Correction** - Bug fix
- 💥 **Breaking change** - Changement incompatible
- 🔬 **Recherche** - Travail d'investigation technique
- 📋 **Documentation** - Mise à jour docs
- ⚡ **Performance** - Optimisation
- 🔐 **Sécurité** - Amélioration sécurité
- 🎉 **Milestone** - Version majeure
