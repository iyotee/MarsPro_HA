# Changelog

Toutes les modifications notables de ce projet seront documentées dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/),
et ce projet adhère au [Versioning Sémantique](https://semver.org/spec/v2.0.0.html).

## [2.2.0] - 2024-12-19 - Mars Hydro MarsPro Home Assistant Integration

### 🎯 Nouvelles Fonctionnalités
- **Récupération automatique des PIDs réels** : L'API récupère maintenant automatiquement les vrais PIDs des appareils de l'utilisateur
- **Contrôle par PID spécifique** : Nouvelle méthode `control_device_by_pid()` pour contrôler un appareil par son PID exact
- **Gestion de multiples appareils** : Nouvelles méthodes `get_all_devices()` et `get_device_by_name()`
- **Logging amélioré** : Informations détaillées sur les appareils trouvés (nom, PID, statut, type)

### 🔧 Améliorations Techniques
- Refactorisation de `toggle_switch()` et `set_brightness()` pour utiliser les PIDs réels
- Test automatique avec les vrais appareils de l'utilisateur dans `test_outletctrl_format.py`
- Gestion intelligente de la sélection d'appareils (automatique si un seul, choix manuel si plusieurs)
- Meilleure gestion des erreurs et messages informatifs

### 🏗️ Architecture
- Centralisation du contrôle dans `control_device_by_pid()`
- Maintien de la compatibilité avec l'API existante
- Fallback automatique vers l'API legacy si nécessaire

### 📋 Format de Contrôle
- Utilisation du format `outletCtrl` validé et fonctionnel
- Structure confirmée : `{"method": "outletCtrl", "params": {"pid": "REAL_PID", "num": 0, "on": 0/1, "pwm": 0-100}}`
- Endpoint confirmé : `/api/upData/device`

## [2.1.1] - 2025-01-31 - Format de Contrôle Réel Implémenté

### 🎯 Découverte Majeure : Format Exact Capturé
- **Format de contrôle réel** découvert via analyse réseau en direct
- **Structure `upDataStatus`** exacte implémentée
- **Endpoint de contrôle confirmé** : `/api/upData/device`
- **Différence cruciale Bluetooth vs WiFi** identifiée

### 📊 Format de Données Réel Implémenté
- **Structure exacte** : `method: "upDataStatus"`, `pid: "345F45EC73C1"`
- **Paramètres réels** : `lastBright`, `switch`, `wifi`, `connect`, `timezone`, `UTC`
- **Headers précis** : User-Agent `Dart/3.4 (dart:io)`, `systemdata` complet
- **Payload JSON** : Format double-encoded comme dans l'app réelle

### 🔍 Découverte Bluetooth vs WiFi
- **Mode Bluetooth** : Communication via API cloud → interceptable ✅
- **Mode WiFi** : Communication directe locale → non interceptable ❌
- **Impact utilisateur** : Intégration fonctionne mieux en mode Bluetooth
- **Documentation** : Guide spécialisé créé

### 🛠️ Améliorations Techniques
- **API MarsPro corrigée** avec format exact capturé
- **Méthodes de contrôle** mises à jour (`toggle_switch`, `set_brightness`, `set_fanspeed`)
- **Logging amélioré** pour diagnostiquer les problèmes de mode
- **Fallback robuste** vers format legacy si nécessaire

### 📁 Nouveaux Fichiers
- `tools/test_real_format_captured.py` - Test avec format exact capturé
- `GUIDE_BLUETOOTH_VS_WIFI_MARSPRO.md` - Guide spécialisé modes de communication

### 🔧 Corrections Apportées
- **Endpoint contrôle** : `/api/upData/device` (au lieu de `/api/android/udm/upData/device/v1`)
- **Structure données** : `upDataStatus` avec `pid` (au lieu de `deviceId`)
- **Paramètres réels** : `lastBright`, `timezone`, `UTC` comme dans l'app
- **Headers systemdata** : Valeurs exactes de l'application réelle

### 🎯 Validation
- ✅ Format exact testé et validé
- ✅ Endpoints confirmés fonctionnels
- ✅ Structure de données conforme à l'app réelle
- ⚠️ Nécessite mode Bluetooth pour fonctionnement optimal

## [2.1.0] - 2025-01-31 - Endpoints MarsPro Réels Découverts

### 🎯 Découvertes Majeures
- **Analyse réseau complète** de l'application MarsPro réelle
- **Identification des vrais endpoints** fonctionnels
- **Domaine confirmé** : `mars-pro.api.lgledsolutions.com`
- **Format d'authentification** et headers exacts découverts

### ✅ Endpoints Confirmés Fonctionnels
- `/api/android/ulogin/mailLogin/v1` (Connexion) - Status 200
- `/api/android/udm/getDeviceList/v1` (Liste dispositifs) - Status 200  
- `/api/android/udm/getDeviceDetail/v1` (Détails dispositif) - Status 200
- `/api/android/mine/info/v1` (Infos utilisateur) - Status 200

### 🔧 Améliorations API MarsPro
- **Headers systemdata** avec paramètres exacts de l'app réelle
- **User-Agent correct** : `Dart/3.4 (dart:io)`
- **Versions et IDs précis** : App 1.3.2, Android 15, etc.
- **Format de réponse standardisé** : `{"code": "000", "msg": "...", "data": {...}}`

### 🛠️ Améliorations Techniques
- **Système de fallback robuste** vers l'API legacy MarsHydro
- **Gestion d'erreurs améliorée** avec codes d'erreur MarsPro
- **Méthodes POST obligatoires** (GET retourne 405)
- **Support dual API** dans l'interface de configuration

### 📁 Nouveaux Fichiers
- `tools/test_real_marspro_discovered.py` - Test des endpoints découverts
- `tools/test_marspro_final_endpoints.py` - Test complet avec vrais identifiants
- `GUIDE_ENDPOINTS_MARSPRO.md` - Documentation complète des découvertes

### 🔍 État Actuel
- ✅ Endpoints identifiés et testés (répondent avec Status 200)
- ⚠️ Authentification à valider avec vrais identifiants MarsPro
- 🔄 Format de contrôle des dispositifs à finaliser
- 📊 Mapping des données en cours d'optimisation

### 🚀 Prochaines Actions
1. Test avec identifiants MarsPro réels pour validation complète
2. Affinage des commandes de contrôle (allumer/éteindre/luminosité)
3. Optimisation du mapping des données dispositifs

## [2.0.0] - 2025-01-30 - Support MarsPro Complet

### 🎉 Nouvelles Fonctionnalités
- **Support complet de l'API MarsPro** (nouvelle application Mars Hydro)
- **Interface de configuration améliorée** avec choix d'API
- **Système de fallback automatique** vers l'ancienne API MarsHydro
- **Compatibilité bidirectionnelle** pour tous les utilisateurs

### 🔧 Améliorations Techniques
- **Nouvelle classe `MarsProAPI`** pour la nouvelle application
- **Gestion intelligente des erreurs** avec tentatives multiples
- **Headers et authentification** adaptés à l'API MarsPro
- **Support des appareils Bluetooth et WiFi**

### 📁 Fichiers Modifiés
- `api_marspro.py` - Nouvelle API pour MarsPro
- `config_flow.py` - Interface de choix d'API
- `__init__.py` - Support dual API
- `manifest.json` - Version 2.0.0

### 🧪 Outils de Développement
- Scripts de test et découverte API
- Documentation d'installation mise à jour
- Guide de contribution en français

## [1.0.0] - 2025-01-29 - Version Initiale

### 🎯 Fonctionnalités de Base
- Support de l'API MarsHydro legacy
- Contrôle des lumières et ventilateurs
- Intégration Home Assistant complète
- Interface de configuration simple

---

**Note** : Version 2.0.0 représente une refonte majeure avec ajout du support MarsPro tout en maintenant la compatibilité Mars Hydro Legacy.

### ✅ Validation Définitive des Endpoints et Formats

### 🎯 Découvertes Majeures
- **Format de contrôle confirmé** : `outletCtrl` simple et fonctionnel
- **Tests réussis** : Validation complète avec identifiants réels de l'utilisateur
- **PID de test validé** : `345F45EC73C1` fonctionne parfaitement
- **Toutes les valeurs PWM testées** : 10, 30, 57, 80, 100 - toutes retournent code '000' (succès)

### 📤 Format Final Validé
```json
{
  "data": "{\"method\":\"outletCtrl\",\"params\":{\"pid\":\"345F45EC73C1\",\"num\":0,\"on\":1,\"pwm\":57}}"
}
```

### 🔧 Tests Complets
- ✅ Authentification MarsPro : jeremy.noverraz2@proton.me
- ✅ Endpoint de contrôle : `/api/upData/device`
- ✅ Status HTTP : 200
- ✅ Code API : '000' (succès)
- ✅ Message : 'success'
- ✅ Contrôle PWM : Toutes valeurs (10-100) fonctionnelles

### 📋 Scripts de Test
- `test_outletctrl_format.py` : Test du format final validé
- `test_real_format_captured.py` : Test basé sur les captures d'écran
- Tous les tests retournent un succès complet

### 🎉 État Final
**L'intégration MarsPro est maintenant complètement fonctionnelle et validée !**
