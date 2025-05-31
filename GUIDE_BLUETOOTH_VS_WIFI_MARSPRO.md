# 🔍 Guide Bluetooth vs WiFi MarsPro

## 💡 Découverte Cruciale

**Observation importante** : La manière dont l'application MarsPro communique avec les appareils dépend du mode de connexion.

## 📡 Modes de Communication

### 🔵 Mode Bluetooth
**Quand la lampe est connectée en Bluetooth uniquement :**

✅ **Communication via API Cloud**
- L'app fait des requêtes HTTP vers `mars-pro.api.lgledsolutions.com`
- **Interceptable** via proxy/analyse réseau
- Format de contrôle : `method: "upDataStatus"`
- Endpoint : `/api/upData/device`

📊 **Format de données capturé :**
```json
{
  "data": "{\"method\":\"upDataStatus\",\"pid\":\"345F45EC73C1\",\"page_cnt\":\"2\",\"params\":{\"code\":200},\"uid\":\"17866\",\"vert\":\"1.0\",\"switch\":\"1\",\"wifi\":\"1\",\"connect\":\"0\",\"lastBright\":60,\"timezone\":\"2025-1-31-42:42:41.6\",\"UTC\":1748659622},{\"conf\":\"8\"}"
}
```

### 📶 Mode WiFi  
**Quand la lampe est connectée au WiFi :**

❌ **Communication Directe Locale**
- L'app communique **directement** avec la lampe via le réseau local
- **Non interceptable** car pas de requêtes HTTP vers le cloud
- Communication probable via TCP/UDP direct ou protocole propriétaire

## 🎯 Implications pour le Développement

### ✅ Ce qui Fonctionne (Mode Bluetooth)
- **Contrôle via API cloud** : Possible
- **Analyse réseau** : Complète
- **Format de données** : Documenté
- **Intégration Home Assistant** : Réalisable

### ⚠️ Défis (Mode WiFi)
- **Contrôle via API cloud** : Limité ou impossible
- **Communication locale** : Protocole inconnu
- **Intégration Home Assistant** : Plus complexe

## 🛠️ Solutions d'Implémentation

### 1. 🎯 Priorité : Support Mode Bluetooth
Notre intégration actuelle fonctionne pour les appareils en mode Bluetooth :
- ✅ Format de données correct implémenté
- ✅ Endpoint réel utilisé (`/api/upData/device`)
- ✅ Structure `upDataStatus` conforme

### 2. 🔄 Mode WiFi : Approches Possibles

#### Option A : Forcer Mode Bluetooth
- Demander à l'utilisateur de déconnecter le WiFi de la lampe
- Utiliser uniquement la connexion Bluetooth
- Contrôle via API cloud

#### Option B : Communication Locale (Avancé)
- Analyser le protocole de communication locale
- Implémenter un client direct vers la lampe
- Scanning réseau pour découvrir les appareils

#### Option C : Mode Hybride
- Détecter le mode de connexion
- Utiliser API cloud si Bluetooth, communication locale si WiFi
- Fallback automatique

## 📝 Format de Données Confirmé

### 🔧 Structure upDataStatus (Réelle)
```json
{
  "method": "upDataStatus",
  "pid": "345F45EC73C1",        // Serial number appareil
  "page_cnt": "2",              // Compteur page
  "params": {"code": 200},      // Paramètres base
  "uid": "17866",               // User ID
  "vert": "1.0",                // Version
  "switch": "1",                // 0=OFF, 1=ON
  "wifi": "1",                  // Statut WiFi
  "connect": "0",               // Statut connexion
  "lastBright": 60,             // Luminosité (si applicable)
  "timezone": "2025-1-31-42:42:41.6",  // Timestamp local
  "UTC": 1748659622             // Timestamp UTC
}
```

### 🎛️ Paramètres de Contrôle
- **Allumer/Éteindre** : `"switch": "1"/"0"`
- **Luminosité** : `"lastBright": <0-100>`
- **Vitesse Ventilateur** : `"fanSpeed": <0-100>` (hypothèse)

## 🧪 Tests et Validation

### ✅ Test Mode Bluetooth
```bash
# Déconnecter la lampe du WiFi (garder Bluetooth)
python tools/test_marspro_final_endpoints.py
```

### 📊 Résultats Attendus
- **Mode Bluetooth** : Contrôle fonctionnel via API cloud
- **Mode WiFi** : Échec du contrôle cloud (normal)

## 🚀 Recommandations

### 1. 🎯 Documentation Utilisateur
Expliquer que l'intégration fonctionne mieux en mode Bluetooth :
- Déconnecter le WiFi de la lampe
- Garder la connexion Bluetooth avec le téléphone
- L'intégration utilisera l'API cloud

### 2. 🔄 Détection Automatique
Implémenter une détection pour informer l'utilisateur :
```python
if control_failed:
    _LOGGER.warning("Control failed. Device might be in WiFi mode. Try Bluetooth-only mode.")
```

### 3. 📈 Évolution Future
- Phase 1 : Support Bluetooth complet ✅
- Phase 2 : Analyse protocole WiFi local
- Phase 3 : Support hybride Bluetooth/WiFi

## 💡 Conclusion

**Votre découverte est fondamentale** : elle explique pourquoi certains utilisateurs ont des difficultés selon leur configuration réseau. Notre implémentation actuelle est optimisée pour le mode Bluetooth, qui est le plus fiable pour une intégration Home Assistant.

---

✅ **Statut** : Mode Bluetooth entièrement supporté avec format de données réel capturé ! 