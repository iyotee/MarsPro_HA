# Changelog

Toutes les modifications notables de ce projet seront documentées dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/),
et ce projet adhère au [Versioning Sémantique](https://semver.org/spec/v2.0.0.html).

## Version 2.3.0 (2025-01-31) - SUPPORT BLUETOOTH BLE HYBRIDE 🔵

### 🎯 **NOUVEAUTÉS MAJEURES**
- **Support Bluetooth BLE direct** pour appareils MarsPro Bluetooth
- **Détection automatique** du mode appareil (Bluetooth vs WiFi)
- **Contrôle hybride** : BLE direct si Bluetooth, Cloud API si WiFi
- **Fallback intelligent** : API cloud si BLE échoue

### 🔧 **AMÉLIORATIONS TECHNIQUES**
- Ajout dépendance `bleak` pour communication Bluetooth Low Energy
- Nouvelles méthodes dans `api_marspro.py` :
  - `detect_device_mode()` : Détection automatique du type d'appareil
  - `control_device_hybrid()` : Contrôle unifié Bluetooth + WiFi
  - `_ble_control_device()` : Communication BLE directe
- Mise à jour `light.py` pour utiliser le contrôle hybride
- Version manifest : 2.3.0

### 🔵 **SUPPORT BLUETOOTH**
- **Scan automatique** des appareils BLE MarsPro
- **Connexion directe** via Bluetooth (comme l'app MarsPro officielle)
- **Communication locale** sans besoin d'internet
- **Protocole BLE** avec commandes multiples et retry automatique

### 📶 **COMPATIBILITÉ WIFI**
- **Maintien total** de la compatibilité WiFi/Cloud existante
- **Activation automatique** avec `setDeviceActiveV` avant contrôle
- **API cloud optimisée** pour appareils WiFi

### 🛠️ **CORRECTIONS**
- Résolution du problème **"lampe ne réagit pas"** pour appareils Bluetooth
- **Détection PID automatique** avec extraction depuis le nom d'appareil
- **Gestion d'erreurs améliorée** avec fallback multi-niveaux

### 💡 **UTILISATION**
- **Installation** : Copier `custom_components/marshydro` dans HA
- **Configuration** : Email/mot de passe MarsPro (comme avant)
- **Détection automatique** : L'intégration choisit Bluetooth ou WiFi
- **Aucun changement** requis pour les utilisateurs existants

---

## Version 2.2.0 (2025-01-30) - DÉCOUVERTE AUTOMATIQUE DES PIDS

### 🎯 **NOUVEAUTÉS**
- **Récupération automatique des PIDs** d'appareils réels
- **Découverte intelligente** avec `deviceProductGroup: 1`
- **Extraction PID** depuis les noms d'appareils (regex)
- **Contrôle par PID** avec `control_device_by_pid()`

### 🔧 **AMÉLIORATIONS**
- Nouvelle méthode `get_all_devices()` avec pagination
- Méthode `get_device_by_name()` pour recherche par nom
- Support des vrais PIDs extraits dynamiquement
- Centralisation du contrôle avec maintien compatibilité

### 🛠️ **CORRECTIONS**
- Endpoints corrigés avec captures réseau réelles
- Headers et payloads exacts de l'app MarsPro
- Gestion des erreurs et retry automatique

---

## Version 2.1.0 (2025-01-29) - ENDPOINTS DÉCOUVERTS

### 🔧 **AMÉLIORATIONS MAJEURES**
- **Endpoints réels** découverts via analyse réseau
- **Headers authentiques** copiés de l'app MarsPro
- **URL de base correcte** : `mars-pro.api.lgledsolutions.com`
- **Payload format exact** basé sur captures HTTP

### 📡 **ENDPOINTS CONFIRMÉS**
- Login : `/api/android/ulogin/mailLogin/v1`
- Liste appareils : `/api/android/udm/getDeviceList/v1`
- Contrôle : `/api/upData/device`
- Info compte : `/api/android/mine/info/v1`

### 🛠️ **CORRECTIONS**
- Authentification fonctionnelle avec vrais paramètres
- Systemdata conforme à l'app officielle
- Gestion des codes de réponse MarsPro

---

## Version 2.0.0 (2025-01-28) - MIGRATION MARSPRO

### 🎯 **CHANGEMENT MAJEUR**
- **Migration complète** de MarsHydro vers MarsPro API
- **Nouvelle authentification** par email/mot de passe
- **Architecture modernisée** pour compatibilité future

### 🔧 **NOUVELLES FONCTIONNALITÉS**
- Support des appareils MarsPro dernière génération
- API unifiée pour lampes et ventilateurs
- Gestion d'erreurs améliorée
- Fallback automatique vers ancienne API si nécessaire

### 📱 **COMPATIBILITÉ**
- Support des anciens appareils MarsHydro (fallback)
- Migration transparente pour utilisateurs existants
- Nouvelles fonctionnalités pour appareils MarsPro

---

## Version 1.x.x - HISTORIQUE MARSHYDRO

### Versions précédentes
- Support API MarsHydro classique
- Authentification par token
- Fonctionnalités de base lampes/ventilateurs
