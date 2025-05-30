# Changelog

Toutes les modifications notables de ce projet seront documentées dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/),
et ce projet adhère au [Versioning Sémantique](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2025-01-31

### ✨ Ajouté
- **Support complet MarsPro API** - Nouvelle intégration pour l'application MarsPro
- **Configuration dual API** - Choix entre MarsPro et Mars Hydro Legacy
- **Fallback automatique** - Basculement transparent entre les APIs
- **Interface de configuration améliorée** - Sélection d'API dans Home Assistant
- **Documentation française complète** - README, guides et exemples
- **Support HACS** - Installation via HACS avec métadonnées complètes

### 🔄 Modifié
- **Architecture API** - Refonte complète pour supporter dual API
- **Flow de configuration** - Interface utilisateur améliorée
- **Gestion d'erreurs** - Messages d'erreur plus clairs et informatifs
- **Code quality** - Refactorisation et optimisations

### 🐛 Corrigé
- **Compatibilité MarsPro** - Résolution des problèmes avec la nouvelle API
- **Authentification** - Amélioration de la robustesse de la connexion
- **Synchronisation** - Meilleure gestion des états temps réel

## [1.0.0] - 2024-XX-XX

### ✨ Initial Release
- Support Mars Hydro Legacy API
- Contrôle lumières et ventilateurs
- Intégration Home Assistant de base
- Entités automatiques
- Configuration YAML

---

**Note** : Version 2.0.0 représente une refonte majeure avec ajout du support MarsPro tout en maintenant la compatibilité Mars Hydro Legacy.
