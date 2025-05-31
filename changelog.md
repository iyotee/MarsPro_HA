# Changelog

Toutes les modifications notables de ce projet seront documentées dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/),
et ce projet adhère au [Versioning Sémantique](https://semver.org/spec/v2.0.0.html).

## Version 2.3.0 (2025-01-31) - SUPPORT BLUETOOTH BLE HYBRIDE ULTRA-ROBUSTE 🔵

### 🎯 **NOUVEAUTÉS MAJEURES**
- **Support Bluetooth BLE direct ultra-robuste** pour appareils MarsPro Bluetooth
- **Détection automatique multi-méthodes** du mode appareil (Bluetooth vs WiFi)
- **Contrôle hybride intelligent** : BLE direct si Bluetooth, Cloud API si WiFi
- **Fallback cascadé** : 4 niveaux de fallback pour assurer le fonctionnement

### 🔧 **AMÉLIORATIONS TECHNIQUES ULTRA-COMPLÈTES**
- Ajout dépendance `bleak` pour communication Bluetooth Low Energy
- **Nouvelles méthodes avancées** dans `api_marspro.py` :
  - `_enhanced_ble_detection()` : Détection BLE multi-techniques
  - `_extended_ble_scan()` : Scan étendu 20 secondes avec patterns flexibles
  - `_pattern_based_ble_scan()` : Recherche par patterns MarsPro connus
  - `_mac_based_ble_scan()` : Détection par fragments d'adresse MAC
  - `control_device_hybrid()` : Contrôle ultra-robuste avec 5 niveaux de fallback
  - `_activate_device_for_cloud()` : Activation préalable cruciale pour Bluetooth
  - `_try_alternative_control_formats()` : Formats de contrôle alternatifs
- **Protocoles BLE multiples** : 7 protocoles différents testés automatiquement
- **Caractéristiques BLE complètes** : Test sur toutes les caractéristiques d'écriture
- Version manifest : 2.3.0

### 🔵 **SUPPORT BLUETOOTH ULTRA-AVANCÉ**
- **4 techniques de scan BLE** :
  1. Scan standard (10s) - correspondance exacte
  2. Scan étendu (20s) - patterns flexibles  
  3. Scan par patterns (15s) - mots-clés MarsPro
  4. Scan MAC (15s) - fragments d'adresse
- **7 protocoles BLE** testés automatiquement sur chaque appareil
- **Connexion directe persistante** via Bluetooth (comme l'app MarsPro officielle)
- **Communication locale ultra-rapide** sans besoin d'internet
- **Debug complet** avec logs détaillés de tous les appareils BLE

### 📶 **COMPATIBILITÉ WIFI RENFORCÉE**
- **Activation automatique systématique** avec `setDeviceActiveV` avant contrôle
- **API cloud optimisée** pour appareils WiFi avec retry intelligent
- **Formats alternatifs** : `upDataStatus`, `deviceControl`, `lightControl`
- **Maintien total** de la compatibilité WiFi/Cloud existante

### 🛠️ **FALLBACK CASCADÉ 5 NIVEAUX**
1. **Bluetooth BLE direct** (si appareil Bluetooth et bleak disponible)
2. **Cloud API avec activation** (méthode principale cloud)
3. **Méthodes legacy** (`set_brightness`, `toggle_switch`)
4. **Formats alternatifs** (3 formats de commande différents)
5. **Détection d'erreur complète** avec diagnostic détaillé

### 💡 **UTILISATION SIMPLIFIÉE**
- **Installation** : Copier `custom_components/marshydro` dans HA (inchangé)
- **Configuration** : Email/mot de passe MarsPro (comme avant)
- **Détection automatique** : L'intégration choisit la meilleure méthode
- **Aucun changement** requis pour les utilisateurs existants
- **Support automatique** des nouveaux appareils Bluetooth

### 🧪 **OUTILS DE TEST COMPLETS**
- `test_complete_final.py` : Test ultra-complet de toutes les méthodes
- Scan BLE détaillé avec liste de tous les appareils
- Diagnostic complet du mode d'appareil
- Tests de tous les niveaux de fallback

### 🔧 **RÉSOLUTION PROBLÈMES**
- ✅ **"Lampe ne réagit pas"** → Résolu pour appareils Bluetooth
- ✅ **"Appareil non détecté en BLE"** → 4 méthodes de détection
- ✅ **"Connexion intermittente"** → Fallback cascadé intelligent
- ✅ **"Incompatibilité protocole"** → 7 protocoles BLE + 3 formats cloud

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
