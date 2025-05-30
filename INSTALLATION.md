# 🚀 Guide d'Installation - Intégration Mars Hydro/MarsPro pour Home Assistant

## 📋 Pré-requis

- **Home Assistant** 2023.1 ou plus récent
- **HACS** (Home Assistant Community Store) installé
- Compte **Mars Hydro** ou **MarsPro** avec appareils configurés

## 🔧 Installation

### Méthode 1: Installation via HACS (Recommandée)

1. **Ouvrir HACS** dans Home Assistant
2. **Aller dans "Intégrations"**
3. **Cliquer sur les trois points ⋮** en haut à droite
4. **Sélectionner "Dépôts personnalisés"**
5. **Ajouter le dépôt** :
   - URL : `https://github.com/iyotee/MarsPro_HA`
   - Catégorie : `Intégration`
6. **Rechercher "Mars Hydro"** dans HACS
7. **Installer l'intégration**
8. **Redémarrer Home Assistant**

### Méthode 2: Installation manuelle

1. **Télécharger** le dossier `custom_components/marshydro/`
2. **Copier** dans `/config/custom_components/marshydro/`
3. **Redémarrer Home Assistant**

## ⚙️ Configuration

### Étape 1: Ajouter l'intégration

1. **Aller dans** `Paramètres > Appareils et services`
2. **Cliquer sur** `+ Ajouter une intégration`
3. **Rechercher** "Mars Hydro"
4. **Sélectionner** l'intégration

### Étape 2: Configuration des paramètres

Remplir le formulaire avec :

#### 📧 **Email**
Votre adresse email Mars Hydro/MarsPro

#### 🔒 **Mot de passe**
Votre mot de passe Mars Hydro/MarsPro

#### 🔄 **Type d'API**
Choisir selon votre application :

- **`MarsPro (Nouvelle application)`** ✅ **RECOMMANDÉ**
  - Pour les utilisateurs de la nouvelle app MarsPro
  - Endpoints découverts : `api.lgledsolutions.com/api/marspro`
  - Fallback automatique vers l'ancienne API si échec

- **`MarsHydro (Ancienne application)`** ⚠️ **LEGACY**
  - Pour les utilisateurs de l'ancienne app MarsHydro
  - ⚠️ Peut déconnecter votre application mobile

## 🎯 Appareils Supportés

### 💡 **Éclairages LED**
- **Entités créées** :
  - `light.mars_[nom_appareil]` - Contrôle ON/OFF + Luminosité
  - `sensor.mars_[nom_appareil]_brightness` - État de la luminosité

### 🌀 **Ventilateurs**
- **Entités créées** :
  - `fan.mars_[nom_appareil]` - Contrôle ON/OFF + Vitesse
  - `sensor.mars_[nom_appareil]_temperature` - Température
  - `sensor.mars_[nom_appareil]_humidity` - Humidité
  - `sensor.mars_[nom_appareil]_speed` - Vitesse actuelle

## 🔍 Dépannage

### ❌ **Erreur "cannot_connect"**

**Causes possibles :**
- Identifiants incorrects
- Compte non enregistré avec MarsPro
- Problème de réseau

**Solutions :**
1. **Vérifier les identifiants** dans l'application mobile
2. **Créer un compte MarsPro** si vous n'en avez pas
3. **Essayer l'autre type d'API** (MarsHydro au lieu de MarsPro)

### ⚠️ **Pas d'appareils détectés**

**Solutions :**
1. **Vérifier** que vos appareils sont connectés dans l'app mobile
2. **Attendre** 2-3 minutes après la configuration
3. **Redémarrer** Home Assistant
4. **Changer le type d'API** dans les options

### 🔄 **Déconnexion de l'app mobile**

**Normal avec l'API MarsHydro legacy** - Un seul appareil peut être connecté simultanément.

**Solutions :**
- Utiliser l'API MarsPro (pas ce problème)
- Accepter la limitation avec l'API legacy

### 📋 **Logs de débogage**

Ajouter dans `configuration.yaml` :

```yaml
logger:
  default: warning
  logs:
    custom_components.marshydro: debug
```

Puis redémarrer Home Assistant et consulter les logs dans `Paramètres > Système > Logs`

## 🆕 Fonctionnalités Avancées

### 🔄 **Fallback Automatique**
Si l'API MarsPro échoue, l'intégration bascule automatiquement vers l'API MarsHydro legacy.

### 🛠️ **Options de Configuration**
Modifier via `Paramètres > Appareils et services > Mars Hydro > Configurer` :
- **Intervalle de mise à jour** (30s par défaut)
- **Type d'API** (changement à chaud possible)

### 📊 **Surveillance**
Les entités remontent des informations détaillées :
- État de connexion
- Dernière mise à jour
- Codes d'erreur API

## 🔧 Outils de Développement

Pour les développeurs et tests avancés :

### 🧪 **Script de Test**
```bash
python tools/test_integration_standalone.py
```

### 🔍 **Découverte d'API**
```bash
python tools/api_discovery.py
```

## 📱 Applications Supportées

| Application | Support | Statut | Notes |
|-------------|---------|---------|-------|
| **MarsPro** | ✅ Plein | Stable | Recommandé |
| **MarsHydro** | ✅ Plein | Legacy | Peut déconnecter mobile |

## 🆘 Support

### 🐛 **Signaler un Bug**
- [Issues GitHub](https://github.com/iyotee/MarsPro_HA/issues)
- Inclure les logs de débogage
- Préciser le type d'API utilisé

### 💬 **Communauté**
- [Forum Home Assistant](https://community.home-assistant.io/)
- [Discord Home Assistant France](https://discord.gg/homeassistant-france)

### 📚 **Documentation**
- [README](README_MarsPro.md) - Vue d'ensemble
- [CHANGELOG](changelog.md) - Historique des versions
- [Code Source](https://github.com/iyotee/MarsPro_HA)

## ✅ Checklist Post-Installation

- [ ] Intégration ajoutée avec succès
- [ ] Appareils détectés dans `Paramètres > Appareils et services`
- [ ] Entités visibles dans `États de développement`
- [ ] Contrôle fonctionnel depuis l'interface
- [ ] Logs sans erreurs critiques

---

🎉 **Félicitations !** Votre intégration Mars Hydro/MarsPro est maintenant opérationnelle ! 