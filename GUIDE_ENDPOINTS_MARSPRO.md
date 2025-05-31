# 🔍 Guide des Endpoints MarsPro Découverts

## 📊 Résumé des Découvertes

Grâce à l'analyse réseau de l'application MarsPro réelle, nous avons identifié les **vrais endpoints** et leur fonctionnement.

### 🌐 Domaine Confirmé
```
https://mars-pro.api.lgledsolutions.com
```
> ⚠️ **Important** : Le domaine utilise le sous-domaine `mars-pro.` contrairement à l'ancienne API qui utilisait directement `api.lgledsolutions.com`

## 🎯 Endpoints Fonctionnels Confirmés

### ✅ Endpoints qui Répondent (Status 200)

| Endpoint | Méthode | Statut | Description |
|----------|---------|--------|-------------|
| `/api/android/ulogin/mailLogin/v1` | POST | ✅ 200 | Connexion email/mot de passe |
| `/api/android/udm/getDeviceList/v1` | POST | ✅ 200 | Liste des dispositifs |
| `/api/android/udm/getDeviceDetail/v1` | POST | ✅ 200 | Détails d'un dispositif |
| `/api/android/mine/info/v1` | POST | ✅ 200 | Informations utilisateur |

### ❌ Endpoints Inexistants (Status 404)

| Endpoint | Statut | Note |
|----------|--------|------|
| `/api/android/auth/login` | ❌ 404 | N'existe pas |
| `/api/android/user/login` | ❌ 404 | N'existe pas |

### ⚠️ Endpoints à Confirmer

| Endpoint | Statut Supposé | Note |
|----------|----------------|------|
| `/api/android/udm/upData/device/v1` | 🔍 À tester | Contrôle dispositifs (hypothèse) |

## 📝 Format de Réponse Standard

Tous les endpoints MarsPro utilisent ce format de réponse :

```json
{
  "code": "000",        // "000" = succès, "100" = erreur
  "subCode": null,
  "msg": "success",     // Message descriptif
  "data": {             // Données de réponse
    // Contenu spécifique selon l'endpoint
  }
}
```

### 🔐 Codes d'Erreur Observés

- `"000"` : Succès
- `"100"` : Erreur générale ("Request illegal" / "fail")

## 🛠️ Améliorations Apportées à l'API

### 1. 📡 Endpoints Mis à Jour

```python
self.endpoints = {
    "login": "/api/android/ulogin/mailLogin/v1",          # ✅ Confirmé
    "device_list": "/api/android/udm/getDeviceList/v1",   # ✅ Confirmé  
    "device_detail": "/api/android/udm/getDeviceDetail/v1", # ✅ Confirmé
    "mine_info": "/api/android/mine/info/v1",             # ✅ Confirmé
    "device_control": "/api/android/udm/upData/device/v1" # 🔍 À confirmer
}
```

### 2. 🔧 Headers Corrigés

```python
headers = {
    'Content-Type': 'application/json',
    'User-Agent': 'Dart/3.4 (dart:io)',  # User-Agent exact de l'app
    'systemdata': json.dumps({
        "reqId": "12345678901",
        "appVersion": "1.3.2",           # Version exacte
        "osType": "android",
        "osVersion": "15",               # Version Android exacte
        "deviceType": "SM-S928B",        # Type de device exact
        "deviceId": "AP3A.240905.015.A2", # ID device exact
        "netType": "wifi",
        "wifiName": "unknown",
        "timestamp": "1234567890",
        "timezone": "34",                # Timezone exacte
        "language": "French",
        "token": "..." # Si connecté
    })
}
```

### 3. 🔄 Méthode de Fallback

L'API MarsPro intègre maintenant un système de fallback automatique :

1. **Tentative MarsPro** avec les nouveaux endpoints
2. **Fallback automatique** vers l'ancienne API MarsHydro si échec
3. **Logging détaillé** pour diagnostiquer les problèmes

## 🧪 Tests et Validation

### Script de Test Complet

Utilisez `tools/test_marspro_final_endpoints.py` pour tester :

```bash
python tools/test_marspro_final_endpoints.py
```

### Script de Découverte

Utilisez `tools/test_real_marspro_discovered.py` pour explorer :

```bash
python tools/test_real_marspro_discovered.py
```

## 🚀 Prochaines Étapes

### 1. 🔑 Test avec Vrais Identifiants

Pour finaliser la configuration, il faut tester avec de vrais identifiants MarsPro :

```bash
python tools/test_marspro_final_endpoints.py
```

### 2. 🎯 Affinage du Contrôle

Une fois l'authentification confirmée, affiner :
- Format exact des commandes de contrôle
- Paramètres requis pour chaque type de dispositif
- Gestion des différents types d'appareils (WiFi/Bluetooth)

### 3. 📊 Mapping des Données

Confirmer le mapping entre :
- Réponses API MarsPro ↔ Format Home Assistant
- Champs de données spécifiques à chaque type d'appareil
- États et contrôles disponibles

## 🐛 Problèmes Connus

1. **Authentification** : Format exact des identifiants à confirmer
2. **Contrôle** : Endpoint et format de contrôle à valider
3. **Types d'appareils** : Différenciation WiFi/Bluetooth à affiner

## 💡 Notes Techniques

- **Tous les endpoints nécessitent POST** (GET retourne 405)
- **Headers systemdata obligatoires** pour l'authentification
- **Format JSON strict** requis
- **Gestion d'erreurs robuste** avec fallback automatique

---

✅ **Statut** : API MarsPro partiellement fonctionnelle, nécessite tests avec vrais identifiants pour finalisation. 