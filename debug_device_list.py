#!/usr/bin/env python3
"""
Debug de la récupération des appareils MarsPro
Analyser pourquoi get_all_devices() ne trouve rien
"""

import asyncio
import aiohttp
import json
import time
import random

class MarsProDeviceDebugger:
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
    
    async def debug_device_list_endpoint(self):
        """Debug de l'endpoint de liste des appareils avec différents payloads"""
        
        print(f"\n🔍 DEBUG ENDPOINT LISTE APPAREILS")
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
        
        # Test 1: Payload utilisé actuellement
        print("\n📤 TEST 1: Payload actuel (pageNum/pageSize)")
        payload1 = {
            "pageNum": 1,
            "pageSize": 50
        }
        
        await self.test_device_list_payload(headers, payload1, "Payload actuel")
        
        # Test 2: Payload alternatif (currentPage)
        print("\n📤 TEST 2: Payload alternatif (currentPage)")
        payload2 = {
            "currentPage": 1,
            "type": None,
            "deviceProductGroup": None
        }
        
        await self.test_device_list_payload(headers, payload2, "Payload alternatif")
        
        # Test 3: Payload vide
        print("\n📤 TEST 3: Payload vide")
        payload3 = {}
        
        await self.test_device_list_payload(headers, payload3, "Payload vide")
        
        # Test 4: Avec différents paramètres
        print("\n📤 TEST 4: Avec userId")
        payload4 = {
            "userId": self.user_id,
            "pageNum": 1,
            "pageSize": 50
        }
        
        await self.test_device_list_payload(headers, payload4, "Avec userId")
    
    async def test_device_list_payload(self, headers, payload, description):
        """Tester un payload spécifique pour la liste des appareils"""
        
        print(f"\n   📋 {description}")
        print(f"   Payload: {json.dumps(payload, indent=2)}")
        
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/api/android/udm/getDeviceList/v1"
            
            try:
                async with session.post(url, json=payload, headers=headers, timeout=30) as response:
                    status = response.status
                    
                    try:
                        data = await response.json()
                    except:
                        data = await response.text()
                    
                    print(f"   Status: {status}")
                    print(f"   Response: {json.dumps(data, indent=2, ensure_ascii=False) if isinstance(data, dict) else data}")
                    
                    if status == 200 and isinstance(data, dict):
                        if data.get('code') == '000':
                            devices = data.get('data', {})
                            if isinstance(devices, dict):
                                device_list = devices.get('list', [])
                                total = devices.get('total', 0)
                                print(f"   ✅ Code 000 - {len(device_list)} appareils trouvés (total: {total})")
                                
                                if device_list:
                                    for i, device in enumerate(device_list):
                                        name = device.get('deviceName', 'N/A')
                                        pid = device.get('deviceSerialnum', 'N/A') 
                                        print(f"      {i+1}. {name} (PID: {pid})")
                                else:
                                    print(f"   ⚠️  Liste vide malgré code 000")
                            else:
                                print(f"   ⚠️  Data n'est pas un dict: {type(devices)}")
                        else:
                            print(f"   ❌ Code erreur: {data.get('code')} - {data.get('msg')}")
                    else:
                        print(f"   ❌ Erreur HTTP ou format invalide")
                        
            except Exception as e:
                print(f"   ❌ Exception: {e}")

async def main():
    """Debug principal"""
    print("🔍 DEBUG RÉCUPÉRATION APPAREILS MARSPRO")
    print("=" * 60)
    
    email = input("📧 Email MarsPro: ").strip()
    password = input("🔑 Mot de passe MarsPro: ").strip()
    
    if not email or not password:
        print("❌ Email et mot de passe requis")
        return
    
    debugger = MarsProDeviceDebugger(email, password)
    
    try:
        # 1. Login
        if not await debugger.login():
            print("❌ Échec du login")
            return
        
        # 2. Debug de l'endpoint des appareils
        await debugger.debug_device_list_endpoint()
        
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 