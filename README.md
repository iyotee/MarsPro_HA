# 🌱 MarsHydro Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![Version](https://img.shields.io/badge/version-2.3.0-blue.svg)](https://github.com/your-repo/marshydro-ha)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Integration Home Assistant pour les appareils d'éclairage **MarsHydro** et **MarsPro** avec support **Bluetooth BLE** et cloud.

## 🚀 Fonctionnalités

### ✅ **Support Multi-Protocoles**
- **🔵 Bluetooth BLE** - Contrôle direct et rapide  
- **☁️ Cloud/WiFi** - Contrôle via Internet
- **🔄 Détection automatique** du type d'appareil

### ✅ **Appareils Supportés**
- **MarsPro LED** (MH-DIMBOX-* séries)
- **MarsHydro Legacy** (anciens modèles)
- **Détection automatique** via API MarsPro

### ✅ **Fonctionnalités Home Assistant**
- **💡 Entités Light** avec contrôle luminosité
- **🎛️ Interface graphique** native HA
- **🤖 Automations** complètes
- **📱 Dashboard** intégré

## 📦 Installation

### **Via HACS (Recommandé)**

1. Ouvrir **HACS** dans Home Assistant
2. Aller dans **Intégrations**
3. Menu ⋮ → **Dépôts personnalisés**
4. Ajouter : `https://github.com/your-repo/marshydro-ha`
5. Type : **Intégration**
6. **Installer** MarsHydro
7. **Redémarrer** Home Assistant

### **Installation Manuelle**

1. Télécharger cette repository
2. Copier `custom_components/marshydro` dans votre dossier HA
3. Redémarrer Home Assistant

## ⚙️ Configuration

### **1. Prérequis Bluetooth BLE**

Votre Home Assistant doit avoir accès au Bluetooth BLE :

- **✅ Raspberry Pi 4** - Bluetooth intégré
- **✅ Adaptateur USB BLE** - Sur serveur Linux 
- **✅ ESP32 Bluetooth Proxy** - Via ESPHome

### **2. Ajout de l'Intégration**

1. **Paramètres** → **Appareils et services**
2. **➕ Ajouter une intégration**
3. Rechercher **"MarsHydro"**
4. Saisir vos **credentials MarsPro** :
   - 📧 Email
   - 🔑 Mot de passe
5. **✅ Terminer** - Appareils détectés automatiquement

### **3. Entités Créées**

L'intégration crée automatiquement :

```yaml
# Exemple d'entités créées
light.marspro_led_cloud      # Contrôle via cloud
light.marspro_led_ble        # Contrôle via Bluetooth BLE
```

## 🎮 Utilisation

### **Interface Graphique**

Les appareils apparaissent dans :
- **🏠 Vue d'ensemble** - Cartes light standard
- **💡 Lumières** - Section dédiée
- **⚙️ Appareils** - Configuration avancée

### **Automations**

```yaml
# Exemple automation - Lever du soleil
automation:
  - alias: "MarsPro - Lever du soleil"
    trigger:
      platform: sun
      event: sunrise
    action:
      service: light.turn_on
      target:
        entity_id: light.marspro_led_ble
      data:
        brightness_pct: 100
        transition: 60

# Exemple automation - Soirée
automation:
  - alias: "MarsPro - Mode soirée"
    trigger:
      platform: time
      at: "20:00:00"
    action:
      service: light.turn_on
      target:
        entity_id: light.marspro_led_ble
      data:
        brightness_pct: 30
```

### **Scripts**

```yaml
# Script - Séquence d'éclairage
script:
  marspro_sequence:
    alias: "Séquence MarsPro"
    sequence:
      - service: light.turn_on
        target:
          entity_id: light.marspro_led_ble
        data:
          brightness_pct: 25
      - delay: "00:30:00"
      - service: light.turn_on
        target:
          entity_id: light.marspro_led_ble
        data:
          brightness_pct: 75
      - delay: "00:30:00"
      - service: light.turn_on
        target:
          entity_id: light.marspro_led_ble
        data:
          brightness_pct: 100
```

## 🔧 Configuration Avancée

### **Configuration YAML (Optionnel)**

```yaml
# configuration.yaml
marshydro:
  email: "votre_email@example.com"
  password: "votre_mot_de_passe"
  scan_interval: 30  # secondes
  bluetooth_timeout: 10  # secondes
```

### **Logs de Debugging**

```yaml
# configuration.yaml
logger:
  default: warning
  logs:
    custom_components.marshydro: debug
```

## 🔵 Spécificités Bluetooth BLE

### **Avantages du BLE**
- **⚡ Rapidité** - Contrôle instantané
- **🔋 Économie** - Faible consommation
- **📶 Fiabilité** - Pas de dépendance Internet
- **🏠 Local** - Contrôle direct

### **Configuration Bluetooth**

#### **Raspberry Pi 4**
```bash
# Vérifier Bluetooth
bluetoothctl show

# Si nécessaire, activer
sudo systemctl enable bluetooth
sudo systemctl start bluetooth
```

#### **ESP32 Bluetooth Proxy**
```yaml
# ESPHome config
esphome:
  name: marspro-proxy

esp32:
  board: esp32dev

wifi:
  ssid: "VotreWiFi"
  password: "VotreMotDePasse"

api:
  encryption:
    key: "VotreCle"

bluetooth_proxy:
  active: true
```

## 🚨 Dépannage

### **Problèmes Courants**

#### **❌ Appareils non détectés**
- Vérifier credentials MarsPro dans l'app officielle
- S'assurer que l'appareil est en mode Bluetooth
- Vérifier la portée BLE (~10m)

#### **❌ Contrôle échoué**
- Redémarrer l'intégration
- Vérifier les logs : `Paramètres > Logs`
- Tester via l'app MarsPro officielle

#### **❌ Bluetooth indisponible**
- Vérifier adaptateur BLE : `bluetoothctl show`
- Redémarrer service : `sudo systemctl restart bluetooth`
- Vérifier permissions Home Assistant

### **Support Technique**

1. **📊 Activer les logs debug**
2. **📝 Consulter les logs** dans HA
3. **🐛 Créer une issue** avec logs
4. **💬 Poser une question** dans Discussions

## 🏗️ Architecture Technique

### **Flux de Données**

```
Home Assistant
    ↓
MarsHydro Integration
    ↓
┌─────────────────┬─────────────────┐
│   Cloud API     │  Bluetooth BLE  │
│  (MarsPro)      │   (Direct)      │
└─────────────────┴─────────────────┘
    ↓                       ↓
☁️ Internet              🔵 BLE Radio
    ↓                       ↓
🌐 MarsPro Servers      📱 Appareil Direct
    ↓
💡 Appareil MarsPro
```

### **Composants**

- **`__init__.py`** - Coordinateur principal
- **`light.py`** - Entités lumières  
- **`config_flow.py`** - Configuration UI
- **`api_marspro.py`** - Client API MarsPro
- **`const.py`** - Constantes

## 🤝 Contribution

Contributions bienvenues ! 

1. **🍴 Fork** le projet
2. **🌿 Créer une branche** : `git checkout -b feature/amazing-feature`
3. **✅ Commit** : `git commit -m 'Add amazing feature'`
4. **📤 Push** : `git push origin feature/amazing-feature`
5. **🔄 Pull Request**

## 📜 Changelog

### **v2.3.0** - Version Finale BLE
- ✅ Support Bluetooth BLE complet
- ✅ Détection automatique d'appareils  
- ✅ Interface Home Assistant native
- ✅ Contrôle hybride (cloud + BLE)
- ✅ Configuration via UI

### **v2.2.0** - API MarsPro
- ✅ Intégration API MarsPro
- ✅ Authentification améliorée
- ✅ Détection automatique PIDs

### **v2.0.0** - Refactorisation
- ✅ Support MarsPro + MarsHydro
- ✅ Code moderne Home Assistant
- ✅ Configuration via UI

## 📄 Licence

Ce projet est sous licence **MIT** - voir [LICENSE](LICENSE) pour détails.

## ⭐ Remerciements

- **🏠 Home Assistant** - Plateforme domotique
- **🔵 Bleak** - Librairie Bluetooth BLE Python
- **🌱 MarsHydro/MarsPro** - Matériel d'éclairage
- **👥 Communauté** - Tests et feedback

---

**🌟 Si cette intégration vous aide, n'hésitez pas à mettre une ⭐ !**
