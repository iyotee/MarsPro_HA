# 📋 Changelog - MarsHydro Home Assistant Integration

## 🚀 **v2.3.0** - Version Finale Bluetooth BLE *(2024-01-xx)*

### ✨ **Nouvelles Fonctionnalités**
- **🔵 Support Bluetooth BLE complet** - Contrôle direct des appareils MarsPro
- **🤖 Détection automatique** des appareils (WiFi/cloud + Bluetooth)
- **🏠 Interface Home Assistant native** - Configuration via UI uniquement
- **🔄 Contrôle hybride** - Basculement automatique cloud → BLE
- **📱 Intégration complète** - Entités light avec tous les attributs HA

### 🔧 **Améliorations Techniques**
- **Coordinateur de données** avec mise à jour intelligente
- **Scanner Bluetooth intégré** Home Assistant
- **Gestion d'erreurs robuste** avec fallback automatique
- **Support ESP32 Bluetooth Proxy** via ESPHome
- **Optimisations performances** pour Raspberry Pi

### 🎯 **Spécificités MarsPro**
- **PID automatique** : Extraction depuis `deviceName` (regex `[A-F0-9]{12}`)
- **Séquence de contrôle exacte** : 4 requêtes (outletCtrl → confirmation → upDataStat → heartbeat)
- **Support appareils Bluetooth** : `deviceProductGroup: 1`, `isNetDevice: false`
- **Protocoles BLE multiples** : Test automatique de 7 protocoles différents

### 📦 **Architecture**
- **`__init__.py`** - Coordinateur principal avec scanner BLE
- **`light.py`** - Entités cloud + BLE séparées 
- **`config_flow.py`** - Configuration avec détection Bluetooth
- **`api_marspro.py`** - API complète avec méthodes hybrides

### 🧹 **Nettoyage**
- **Suppression** de tous les fichiers de test/debug
- **README professionnel** avec documentation complète
- **Code optimisé** pour production Home Assistant

---

## 🔥 **v2.2.0** - Intégration API MarsPro *(2024-01-xx)*

### ✨ **Nouvelles Fonctionnalités**
- **API MarsPro native** - Support de la nouvelle application MarsPro
- **Authentification robuste** - Gestion des tokens et renouvellement automatique
- **Détection automatique des PIDs** - Plus besoin de configuration manuelle
- **Endpoints confirmés** - `/api/android/ulogin/mailLogin/v1` et `/api/android/udm/getDeviceList/v1`

### 🔧 **Améliorations**
- **Fallback intelligent** vers API MarsHydro legacy
- **Gestion d'erreurs avancée** - Codes d'erreur spécifiques MarsPro
- **Headers système complets** - systemData avec informations appareil
- **Rate limiting** - Protection contre les appels trop fréquents

### 🎯 **Découvertes Techniques**
- **URL de base confirmée** : `https://mars-pro.api.lgledsolutions.com`
- **User-Agent exact** : `Dart/3.4 (dart:io)`
- **Format systemData** avec reqId, appVersion, deviceType, etc.
- **Support appareils multiples** - Bluetooth et WiFi

---

## 🔄 **v2.1.0** - Reverse Engineering Avancé *(2024-01-xx)*

### 🕵️ **Découvertes Réseau**
- **Analyse HTTP Toolkit** - Capture complète des requêtes MarsPro
- **Endpoints réels découverts** - `/api/android/udm/getDeviceList/v1`
- **Payload exact identifié** - `{"currentPage": 1, "type": null, "deviceProductGroup": 1}`
- **PID confirmé** - `345F45EC73CC` pour appareil test

### 🔧 **Méthodes de Contrôle**
- **Séquence 4 requêtes** basée sur captures réseau réelles
- **Format outletCtrl** - `{"pid": "345F45EC73CC", "num": 0, "on": 1, "pwm": 100}`
- **upDataStat complet** - Payload 601 bytes avec tous les champs
- **Heartbeat final** - Validation et maintien connexion

### 📊 **Tests Extensifs**
- **test_real_brightness_control.py** - Test complet tous niveaux
- **test_wifi_hybrid_device.py** - Tests appareils WiFi/Bluetooth
- **debug_device_list.py** - Analyse endpoints multiples

---

## 🏗️ **v2.0.0** - Refactorisation Majeure *(2024-01-xx)*

### ✨ **Nouvelles Fonctionnalités**
- **Support MarsPro ET MarsHydro** - Deux APIs dans une seule intégration
- **Configuration via UI** - Plus de configuration YAML manuelle
- **Choix automatique d'API** - Détection du type de compte
- **Entités dynamiques** - Création selon le type d'appareil détecté

### 🔧 **Architecture Moderne**
- **Config Flow** complet avec validation
- **Data Update Coordinator** pour optimiser les appels API
- **Gestionnaire d'appareils** avec identifiants stables
- **Support plateformes multiples** - Light, Switch, Fan, Sensor

### 🎯 **Améliorations UX**
- **Interface graphique** pour la configuration
- **Détection automatique** du type d'appareil (Light vs Fan)
- **Fallback intelligent** entre les APIs
- **Messages d'erreur clairs** et debugging amélioré

---

## 🌱 **v1.x** - Versions Legacy

### **v1.2.0** - Support MarsHydro Legacy
- API MarsHydro originale
- Contrôle basique lumières
- Configuration YAML

### **v1.1.0** - Améliorations
- Gestion d'erreurs
- Support ventilateurs
- Optimisations

### **v1.0.0** - Version Initiale
- Première version fonctionnelle
- Support lampes de base
- Intégration Home Assistant basique

---

## 🎯 **Prochaines Versions**

### **v2.4.0** - ESPHome Integration *(Planifié)*
- Support natif ESPHome
- Proxy Bluetooth automatique
- Configuration zero-touch

### **v2.5.0** - Fonctionnalités Avancées *(Planifié)*
- Groupes d'appareils
- Scénarios prédéfinis
- Monitoring avancé

---

**📅 Format des dates** : YYYY-MM-DD  
**🔄 Versioning** : Semantic Versioning (SemVer)  
**📋 Types de changements** : ✨ Nouveau | 🔧 Amélioration | 🐛 Correction | 🗑️ Suppression
