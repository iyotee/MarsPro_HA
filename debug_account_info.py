#!/usr/bin/env python3
"""
Debug complet du compte MarsPro
Explorer d'autres endpoints pour comprendre pourquoi aucun appareil n'est trouvé
"""

import asyncio
import aiohttp
import json
import time
import random

class MarsProAccountDebugger:
    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.token = None
        self.user_id = None
        self.base_url = "https://mars-pro.api.lgledsolutions.com"
        
    async def login(self):
        """Login pour obtenir le token"""
        systemdata = {
            "reqId": str(random.randint(10000000000, 99999999999)),
            "appVersion": "1.3.2",
            "osType": "android", 
            "osVersion": "15",
            "deviceType": "SM-S928B",
            "deviceId": "AP3A.240905.015.A2",
            "netType": "wifi",
            "wifiName": "unknown",
            "timestamp": str(int(time.time())),
            "timezone": "34",
            "language": "French"
        }
        
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Dart/3.4 (dart:io)',
            'systemdata': json.dumps(systemdata)
        }
        
        payload = {
            "email": self.email,
            "password": self.password,
            "loginMethod": "1"
        }
        
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/api/android/ulogin/mailLogin/v1"
            async with session.post(url, json=payload, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('code') == '000':
                        self.token = data['data']['token']
                        self.user_id = data['data']['userId']
                        print(f"✅ Login réussi !")
                        print(f"Token: {self.token[:20]}...")
                        print(f"User ID: {self.user_id}")
                        return True
                    else:
                        print(f"❌ Login échoué: {data}")
                        return False
                else:
                    print(f"❌ HTTP Error: {response.status}")
                    return False
    
    async def explore_all_endpoints(self):
        """Explorer tous les endpoints découverts précédemment"""
        
        print(f"\n🔍 EXPLORATION COMPLÈTE DES ENDPOINTS")
        print("=" * 60)
        
        # Headers avec token
        systemdata = {
            "reqId": str(random.randint(10000000000, 99999999999)),
            "appVersion": "1.3.2",
            "osType": "android",
            "osVersion": "15", 
            "deviceType": "SM-S928B",
            "deviceId": "AP3A.240905.015.A2",
            "netType": "wifi",
            "wifiName": "unknown",
            "timestamp": str(int(time.time())),
            "timezone": "34",
            "language": "French",
            "token": self.token
        }
        
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Dart/3.4 (dart:io)',
            'systemdata': json.dumps(systemdata)
        }
        
        # Test 1: Mine info (informations utilisateur)
        print(f"\n📤 TEST 1: Informations utilisateur")
        await self.test_endpoint(headers, "/api/android/mine/info/v1", {}, "Info utilisateur")
        
        # Test 2: Device detail avec différents IDs
        print(f"\n📤 TEST 2: Détails appareil (test)")
        await self.test_endpoint(headers, "/api/android/udm/getDeviceDetail/v1", 
                                {"deviceId": "345F45EC73C1"}, "Détails appareil avec PID test")
        
        # Test 3: Endpoints de recherche d'appareils
        print(f"\n📤 TEST 3: Autres endpoints de recherche")
        
        # Endpoint potentiel pour les appareils non configurés
        await self.test_endpoint(headers, "/api/android/udm/getUnbindDeviceList/v1", {}, "Appareils non liés")
        
        # Endpoint potentiel pour les groupes
        await self.test_endpoint(headers, "/api/android/udm/getDeviceGroupList/v1", {}, "Groupes d'appareils")
        
        # Test 4: Autres variantes de getDeviceList
        print(f"\n📤 TEST 4: Variantes getDeviceList")
        
        # Sans /v1
        await self.test_endpoint(headers, "/api/android/udm/getDeviceList", 
                                {"pageNum": 1, "pageSize": 50}, "Sans version")
        
        # Avec différents paramètres
        await self.test_endpoint(headers, "/api/android/udm/getDeviceList/v1", 
                                {"status": "online"}, "Avec status online")
        
        await self.test_endpoint(headers, "/api/android/udm/getDeviceList/v1", 
                                {"bindStatus": 1}, "Avec bindStatus")
        
        # Test 5: Endpoints de configuration
        print(f"\n📤 TEST 5: Configuration et bind")
        
        await self.test_endpoint(headers, "/api/android/udm/getBindDeviceList/v1", {}, "Appareils liés")
        
        await self.test_endpoint(headers, "/api/android/udm/searchDevice/v1", 
                                {"keyword": ""}, "Recherche appareils")
    
    async def test_endpoint(self, headers, endpoint, payload, description):
        """Tester un endpoint spécifique"""
        
        print(f"\n   🔗 {description}")
        print(f"   Endpoint: {endpoint}")
        print(f"   Payload: {json.dumps(payload, indent=2) if payload else 'Vide'}")
        
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}{endpoint}"
            
            try:
                async with session.post(url, json=payload, headers=headers, timeout=30) as response:
                    status = response.status
                    
                    try:
                        data = await response.json()
                    except:
                        data = await response.text()
                    
                    print(f"   Status: {status}")
                    
                    if status == 200 and isinstance(data, dict):
                        code = data.get('code', 'N/A')
                        msg = data.get('msg', 'N/A')
                        print(f"   Code: {code} - Message: {msg}")
                        
                        if code == '000':
                            data_content = data.get('data', {})
                            if isinstance(data_content, dict):
                                if 'list' in data_content:
                                    items = data_content['list']
                                    print(f"   ✅ {len(items)} éléments trouvés")
                                    if items:
                                        for i, item in enumerate(items[:3]):  # Afficher max 3 items
                                            print(f"      Item {i+1}: {json.dumps(item, ensure_ascii=False)[:100]}...")
                                elif data_content:
                                    print(f"   ✅ Données: {json.dumps(data_content, ensure_ascii=False)[:200]}...")
                                else:
                                    print(f"   ⚠️  Données vides")
                            else:
                                print(f"   ✅ Data: {str(data_content)[:100]}...")
                        else:
                            print(f"   ❌ Erreur API: {code} - {msg}")
                    elif status == 404:
                        print(f"   ❌ Endpoint non trouvé (404)")
                    elif status == 405:
                        print(f"   ❌ Méthode non autorisée (405)")
                    else:
                        print(f"   ❌ HTTP {status}: {str(data)[:100]}...")
                        
            except Exception as e:
                print(f"   ❌ Exception: {e}")

async def main():
    """Debug principal"""
    print("🔍 DEBUG COMPLET COMPTE MARSPRO")
    print("=" * 60)
    
    email = input("📧 Email MarsPro: ").strip()
    password = input("🔑 Mot de passe MarsPro: ").strip()
    
    if not email or not password:
        print("❌ Email et mot de passe requis")
        return
    
    debugger = MarsProAccountDebugger(email, password)
    
    try:
        # 1. Login
        if not await debugger.login():
            print("❌ Échec du login")
            return
        
        # 2. Explorer tous les endpoints
        await debugger.explore_all_endpoints()
        
        print(f"\n💡 RECOMMANDATIONS:")
        print("1. Vérifiez dans l'app MarsPro que vos appareils sont bien ajoutés")
        print("2. Assurez-vous que les appareils sont en mode Bluetooth (pas WiFi)")
        print("3. Essayez d'ajouter un appareil dans l'app puis relancez ce test")
        
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 