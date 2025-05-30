# 🔍 Guide d'Extraction des Clés Secrètes MarsPro

## 🎯 Objectif
Trouver les paramètres secrets que l'app MarsPro utilise pour se connecter à l'API.

---

## 📥 **ÉTAPE 1 : Télécharger l'APK**

### Option A : APKPure
1. Allez sur **https://apkpure.com**
2. Recherchez **"MarsPro"**
3. Téléchargez la version **1.3.2** (ou la plus récente)
4. Fichier obtenu : `MarsPro_1.3.2.apk`

### Option B : APKMirror  
1. Allez sur **https://apkmirror.com**
2. Recherchez **"MarsPro"** 
3. Téléchargez la dernière version

---

## 📂 **ÉTAPE 2 : Décompresser l'APK**

### Méthode Simple :
1. **Renommez** `MarsPro_1.3.2.apk` → `MarsPro_1.3.2.zip`
2. **Clic droit** → "Extraire ici" (avec 7-Zip, WinRAR, ou Windows)
3. Vous obtenez un dossier `MarsPro_1.3.2/`

---

## 🔍 **ÉTAPE 3 : Chercher les Secrets**

### 📁 Dossiers à explorer en priorité :
```
MarsPro_1.3.2/
├── assets/          ← TRÈS IMPORTANT !
├── res/
│   ├── values/      ← Fichiers XML avec constantes
│   └── raw/         ← Fichiers de config
├── META-INF/        ← Métadonnées
└── classes.dex      ← Code compilé (ignorez)
```

### 🎯 **Fichiers à ouvrir avec Bloc-notes :**
- **Tous les `.txt`**
- **Tous les `.xml`** 
- **Tous les `.json`**
- **Tous les `.properties`**
- **Fichiers sans extension** dans `assets/`

### 🔎 **Mots-clés à chercher** (Ctrl+F) :
```
api.lgledsolutions.com
systemData
loginMethod
appKey
apiKey
signature
deviceId
User-Agent
MarsPro
clientSecret
appSecret
auth
login
```

---

## 💡 **ÉTAPE 4 : Ce qu'on cherche**

### 🎯 **Résultats possibles :**

#### **A) URL d'API complète :**
```xml
<string name="api_url">https://api.lgledsolutions.com/api/marspro/v2/auth/login</string>
```

#### **B) Clés secrètes :**
```xml
<string name="app_key">abc123def456</string>
<string name="api_secret">xyz789uvw012</string>
```

#### **C) User-Agent exact :**
```xml
<string name="user_agent">MarsPro/1.3.2 (Android 11; Build 2023.12.01)</string>
```

#### **D) Headers systémiques :**
```json
{
  "systemData": {
    "appVersion": "1.3.2",
    "osType": "Android",
    "deviceType": "phone"
  }
}
```

---

## ⚡ **ÉTAPE 5 : Test Rapide**

Une fois que vous trouvez des clés, testez-les ici :

```python
# Test avec les nouvelles clés trouvées
payload = {
    "email": "jeremy.noverraz2@proton.me",
    "password": "T00rT00r",
    "appKey": "VOTRE_CLE_TROUVEE",  # ← ICI
    "loginMethod": "1"
}

headers = {
    'User-Agent': 'VOTRE_USER_AGENT_TROUVE',  # ← ICI
    'Content-Type': 'application/json'
}
```

---

## 🎯 **Résultat Espéré**

Vous devriez trouver quelque chose comme :
```xml
<!-- Dans res/values/strings.xml -->
<string name="api_base_url">https://api.lgledsolutions.com/api/marspro</string>
<string name="app_key">lg_mars_pro_2023_v132</string>
<string name="client_secret">mp_android_secret_key_2023</string>
```

---

## 💪 **Si vous trouvez les clés :**
1. **Copiez-les** dans un fichier texte
2. **Dites-moi** ce que vous avez trouvé
3. Je mettrai à jour l'intégration avec les bons paramètres
4. **🎉 SUCCÈS GARANTI !**

---

## ❓ **Aide :**
- **Trop de fichiers ?** → Concentrez-vous sur `assets/` et `res/values/`
- **Rien trouvé ?** → Cherchez "lgledsolutions" dans TOUS les fichiers
- **Bloqué ?** → Partagez le nom des fichiers que vous voyez

**⏱️ Temps estimé : 5-15 minutes maximum !** 