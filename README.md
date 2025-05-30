# Mars Hydro Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![GitHub Latest Release](https://img.shields.io/github/release/votre-username/marspro-homeassistant.svg)](https://github.com/votre-username/marspro-homeassistant/releases)
[![GitHub All Releases](https://img.shields.io/github/downloads/votre-username/marspro-homeassistant/total.svg)](https://github.com/votre-username/marspro-homeassistant/releases)

🌱 **Intégration Home Assistant pour les équipements Mars Hydro et MarsPro**

Cette intégration permet de contrôler vos lampes de culture et ventilateurs Mars Hydro directement depuis Home Assistant, avec support complet pour les nouvelles API MarsPro.

## 🚀 Fonctionnalités

### ✅ Support Complet
- **🔥 MarsPro (Nouvelle API)** - Support natif de la nouvelle application MarsPro
- **🏛️ Mars Hydro Legacy** - Compatibilité avec l'ancienne API Mars Hydro
- **🔄 Fallback Automatique** - Bascule automatiquement entre les APIs si nécessaire

### 🎛️ Contrôles Disponibles
- **💡 Lampes de Culture**
  - Allumer/Éteindre
  - Contrôle de la luminosité (0-100%)
  - État temps réel
- **🌪️ Ventilateurs**
  - Allumer/Éteindre  
  - Contrôle de la vitesse
  - Monitoring température/humidité

### 🏠 Intégration Home Assistant
- **Entités automatiques** - Lampes et ventilateurs ajoutés automatiquement
- **Automatisations** - Programmez vos cycles de culture
- **Interface graphique** - Contrôle via l'interface Home Assistant
- **État en temps réel** - Synchronisation automatique

## 📦 Installation

### Via HACS (Recommandé)
1. Ouvrez HACS dans Home Assistant
2. Allez dans "Intégrations"
3. Cliquez sur "⋮" puis "Dépôts personnalisés"
4. Ajoutez cette URL : `https://github.com/votre-username/marspro-homeassistant`
5. Catégorie : "Integration"
6. Redémarrez Home Assistant

### Installation Manuelle
1. Téléchargez le dossier `custom_components/marshydro`
2. Copiez-le dans `<config>/custom_components/`
3. Redémarrez Home Assistant

## ⚙️ Configuration

### Via Interface Home Assistant
1. Allez dans **Configuration** > **Intégrations**
2. Cliquez **Ajouter une intégration**
3. Cherchez **"Mars Hydro"**
4. Choisissez votre type d'API :
   - **MarsPro** (recommandé pour nouveaux comptes)
   - **Mars Hydro Legacy** (anciens comptes)
5. Entrez vos identifiants

### Via Configuration YAML
```yaml
# configuration.yaml
marshydro:
  email: "votre@email.com"
  password: "votre_mot_de_passe"
  api_type: "marspro"  # ou "legacy"
```

## 🎯 Exemples d'Utilisation

### Automatisation de Culture
```yaml
# Cycle jour/nuit automatique
automation:
  - alias: "Culture - Lever du soleil"
    trigger:
      platform: time
      at: "07:00:00"
    action:
      - service: light.turn_on
        target:
          entity_id: light.mars_hydro_grow_light
        data:
          brightness_pct: 80
      - service: fan.turn_on
        target:
          entity_id: fan.mars_hydro_ventilator

  - alias: "Culture - Coucher du soleil"
    trigger:
      platform: time
      at: "22:00:00"
    action:
      - service: light.turn_off
        target:
          entity_id: light.mars_hydro_grow_light
      - service: fan.turn_off
        target:
          entity_id: fan.mars_hydro_ventilator
```

### Dashboard Lovelace
```yaml
# Carte contrôle de culture
type: entities
title: "🌱 Culture Mars Hydro"
entities:
  - entity: light.mars_hydro_grow_light
  - entity: fan.mars_hydro_ventilator
  - entity: sensor.mars_hydro_temperature
  - entity: sensor.mars_hydro_humidity
```

## 🔧 Résolution de Problèmes

### Erreurs de Connexion
- **Code 100** : Identifiants incorrects
- **SSL Error** : Problème de connectivité réseau
- **Fallback activé** : Passage automatique à l'API legacy

### Compte MarsPro
1. Téléchargez l'app **MarsPro** (Android/iOS)
2. Créez un compte avec votre email
3. Connectez vos appareils dans l'app
4. Utilisez les mêmes identifiants dans Home Assistant

### Logs de Debug
```yaml
# configuration.yaml
logger:
  logs:
    custom_components.marshydro: debug
```

## 📱 Applications Supportées

| Application | API Type | Status |
|-------------|----------|--------|
| **MarsPro** (Nouvelle) | `marspro` | ✅ Supporté |
| **Mars Hydro** (Legacy) | `legacy` | ✅ Supporté |

## 🏗️ Architecture Technique

- **Backend** : Firebase + REST API
- **Endpoints** : `api.lgledsolutions.com`
- **Auth** : Google OAuth + Email/Password
- **Fallback** : Basculement automatique entre APIs
- **Sync** : Temps réel avec rate limiting

## 🤝 Contribution

Les contributions sont les bienvenues ! 

1. Fork le projet
2. Créez une branche (`git checkout -b feature/nouvelle-fonctionnalite`)
3. Commit vos changements (`git commit -m 'Ajout nouvelle fonctionnalité'`)
4. Push vers la branche (`git push origin feature/nouvelle-fonctionnalite`)
5. Ouvrez une Pull Request

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

## ⭐ Support

Si cette intégration vous aide, n'hésitez pas à ⭐ ce repo !

Pour les problèmes et suggestions : [Issues GitHub](https://github.com/votre-username/marspro-homeassistant/issues)

---

**🌱 Cultivez intelligemment avec Home Assistant ! 🏠**
