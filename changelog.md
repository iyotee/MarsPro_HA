# Changelog

Toutes les modifications notables de ce projet seront documentées dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/),
et ce projet adhère au [Versioning Sémantique](https://semver.org/spec/v2.0.0.html).

## Version 2.3.0 (2025-01-31) - SUPPORT BLUETOOTH BLE HYBRIDE ULTRA-ROBUSTE 🔵

### 🎯 **NOUVEAUTÉS MAJEURES**
- **Support Bluetooth BLE direct ultra-robuste** pour appareils MarsPro Bluetooth
- **Détection automatique multi-méthodes** du mode appareil (Bluetooth vs WiFi)
- **Contrôle hybride optimisé** : **WiFi Cloud prioritaire**, BLE en fallback
- **Configuration WiFi automatique** : Script pour convertir Bluetooth → WiFi
- **Fallback cascadé** : 4 niveaux de fallback pour assurer le fonctionnement

### 🌟 **DÉCOUVERTE IMPORTANTE**
**Une fois configuré en WiFi, l'appareil MarsPro abandonne le Bluetooth et utilise exclusivement le cloud !**
- ✅ **Mode WiFi = Contrôle fiable et instantané**
- ✅ **Script `configure_wifi_marspro.py`** pour conversion automatique
- ✅ **Priorisation Cloud WiFi** dans l'intégration pour performance optimale

### 🔧 **AMÉLIORATIONS TECHNIQUES ULTRA-COMPLÈTES**
- Ajout dépendance `bleak` pour communication Bluetooth Low Energy
- **Nouvelles méthodes avancées** dans `api_marspro.py` :
  - `control_device_hybrid()` : **Contrôle WiFi-prioritaire** optimisé
  - `_enhanced_ble_detection()` : Détection BLE multi-techniques (fallback)
  - `_extended_ble_scan()` : Scan étendu 20 secondes avec patterns flexibles
  - `_pattern_based_ble_scan()` : Recherche par patterns MarsPro connus
  - `_mac_based_ble_scan()` : Détection par fragments d'adresse MAC
  - `_activate_device_for_cloud()` : Activation préalable cruciale
  - `_try_alternative_control_formats()` : Formats de contrôle alternatifs
- **Protocoles BLE multiples** : 7 protocoles différents testés automatiquement
- **Script de configuration WiFi** : `configure_wifi_marspro.py`
- Version manifest : 2.3.0-final

### 📶 **PRIORITÉ WIFI CLOUD (RECOMMANDÉ)**
- **🥇 PRIORITÉ 1** : Cloud API avec activation `setDeviceActiveV`
- **🥈 PRIORITÉ 2** : Bluetooth BLE direct (si échec WiFi)
- **🥉 PRIORITÉ 3** : Méthodes legacy (`set_brightness`, `toggle_switch`)
- **🏅 PRIORITÉ 4** : Formats alternatifs en dernière chance

### 🔵 **SUPPORT BLUETOOTH ULTRA-AVANCÉ (FALLBACK)**
- **4 techniques de scan BLE** :
  1. Scan standard (10s) - correspondance exacte
  2. Scan étendu (20s) - patterns flexibles  
  3. Scan par patterns (15s) - mots-clés MarsPro
  4. Scan MAC (15s) - fragments d'adresse
- **7 protocoles BLE** testés automatiquement sur chaque appareil
- **Connexion directe persistante** via Bluetooth (fallback si WiFi échoue)
- **Communication locale** sans besoin d'internet
- **Debug complet** avec logs détaillés de tous les appareils BLE

### 🛠️ **SCRIPT CONFIGURATION WIFI**
- **`configure_wifi_marspro.py`** : Configuration automatique Bluetooth → WiFi
- **Détection mode automatique** : WiFi déjà configuré ou Bluetooth
- **Configuration guidée** : SSID + mot de passe WiFi
- **Test automatique** : Vérification des commandes WiFi/Cloud
- **Support 2.4GHz/5GHz** avec recommandations sécurité

### 💡 **UTILISATION SIMPLIFIÉE**
- **Étape 0 (Recommandée)** : Exécuter `configure_wifi_marspro.py` pour configurer WiFi
- **Installation HA** : Copier `custom_components/marshydro` dans HA (inchangé)
- **Configuration HA** : Email/mot de passe MarsPro (comme avant)
- **Détection automatique** : L'intégration privilégie WiFi, fallback BLE
- **Performance optimale** : WiFi = instantané, BLE = fallback local

### 🧪 **OUTILS DE TEST COMPLETS**
- `configure_wifi_marspro.py` : **Configuration WiFi optimale** (RECOMMANDÉ)
- `test_complete_final.py` : Test ultra-complet de toutes les méthodes
- Scan BLE détaillé avec liste de tous les appareils
- Diagnostic complet du mode d'appareil
- Tests de tous les niveaux de fallback

### 🔧 **RÉSOLUTION PROBLÈMES**
- ✅ **"Lampe ne réagit pas"** → **Configurer en WiFi via script**
- ✅ **"Contrôle intermittent"** → **WiFi prioritaire + fallback BLE**
- ✅ **"Appareil non détecté BLE"** → **WiFi recommandé, 4 méthodes BLE fallback**
- ✅ **"Incompatibilité protocole"** → **4 priorités: WiFi → BLE → Legacy → Alt**

### 🎯 **RECOMMANDATION FINALE**
**CONFIGUREZ VOTRE APPAREIL EN WIFI** avec `configure_wifi_marspro.py` pour :
- 🚀 **Performance optimale** (contrôle instantané)
- 🔄 **Fiabilité maximale** (cloud stable)
- 🏠 **Intégration HA parfaite** (détection automatique WiFi)
- 📱 **Compatibilité totale** (comme app MarsPro officielle)

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
