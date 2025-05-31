#!/usr/bin/env python3
"""
Test du format EXACT capturé dans les captures d'écran MarsPro
Validation du format upDataStatus réel
"""

import asyncio
import aiohttp
import json
import time
import random

class MarsPro_ExactFormat_Tester:
    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.token = None
        self.user_id = None
        self.base_url = "https://mars-pro.api.lgledsolutions.com"
        
    async def login(self):
        """Login avec format exact capturé"""
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
                        print(f"✅ Login réussi ! Token: {self.token[:20]}...")
                        return True
                    else:
                        print(f"❌ Login échoué: {data}")
                        return False
                else:
                    print(f"❌ HTTP Error: {response.status}")
                    return False
    
    async def get_device_list(self):
        """Récupérer la liste des appareils"""
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
        
        payload = {
            "pageNum": 1,
            "pageSize": 50
        }
        
        print(f"\n📤 Requête liste appareils:")
        print(f"URL: {self.base_url}/api/android/udm/getDeviceList/v1")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        print(f"SystemData: {json.dumps(systemdata, indent=2)}")
        
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/api/android/udm/getDeviceList/v1"
            async with session.post(url, json=payload, headers=headers) as response:
                status = response.status
                
                try:
                    data = await response.json()
                except:
                    data = await response.text()
                
                print(f"\n📥 Réponse liste appareils:")
                print(f"Status: {status}")
                print(f"Data complète: {json.dumps(data, indent=2, ensure_ascii=False)}")
                
                if status == 200 and isinstance(data, dict):
                    if data.get('code') == '000':
                        devices = data.get('data', {}).get('list', [])
                        print(f"✅ Trouvé {len(devices)} appareils")
                        
                        # Affichage détaillé des données
                        data_section = data.get('data', {})
                        print(f"\n📊 Détails de la section 'data':")
                        print(f"   - Total: {data_section.get('total', 'N/A')}")
                        print(f"   - Pages: {data_section.get('pages', 'N/A')}")
                        print(f"   - Size: {data_section.get('size', 'N/A')}")
                        print(f"   - Current: {data_section.get('current', 'N/A')}")
                        print(f"   - Records: {data_section.get('records', 'N/A')}")
                        
                        return devices
                    else:
                        print(f"❌ Erreur API: Code {data.get('code')} - {data.get('msg')}")
                        return []
                else:
                    print(f"❌ HTTP Error: {status}")
                    return []
    
    async def test_exact_control_format(self, device_serial, brightness=60):
        """Test du format de contrôle EXACT capturé dans les screenshots"""
        
        print(f"\n🎯 TEST FORMAT EXACT CAPTURÉ")
        print(f"Appareil: {device_serial}")
        print(f"Luminosité: {brightness}%")
        
        # Format EXACT basé sur les captures d'écran !
        inner_data = {
            "method": "upDataStatus",  # Exactement comme capturé
            "pid": device_serial,      # PID comme dans les captures
            "page_cnt": "2",           # Valeur exacte capturée
            "params": {
                "code": 200            # Code exact capturé
            },
            "uid": self.user_id,       # User ID récupéré
            "vert": "1.0",             # Version exacte capturée
            "switch": "1",             # 1=ON pour allumer
            "wifi": "1",               # Statut WiFi capturé
            "connect": "0",            # Statut connexion capturé
            "lastBright": brightness,  # Luminosité comme capturé !
            "timezone": f"{time.strftime('%Y-%m-%d-%H:%M:%S')}.{int(time.time()%1000)}",  # Format timezone capturé
            "UTC": int(time.time())    # Timestamp UTC capturé
        }
        
        # Le payload final doit être exactement comme dans les captures
        payload = {"data": json.dumps(inner_data)}
        
        print(f"\n📤 Payload envoyé (format exact):")
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        
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
        
        # Endpoint EXACT capturé
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/api/upData/device"
            async with session.post(url, json=payload, headers=headers) as response:
                status = response.status
                
                try:
                    response_data = await response.json()
                except:
                    response_data = await response.text()
                
                print(f"\n📥 Réponse reçue:")
                print(f"Status: {status}")
                print(f"Data: {response_data}")
                
                if status == 200 and isinstance(response_data, dict) and response_data.get('code') == '000':
                    print(f"✅ CONTRÔLE RÉUSSI avec format exact !")
                    return True
                else:
                    print(f"❌ Contrôle échoué")
                    return False

async def main():
    """Test principal avec format exact capturé"""
    print("🚀 TEST FORMAT EXACT MARSPRO CAPTURÉ")
    print("=" * 60)
    
    email = input("📧 Email MarsPro: ").strip()
    password = input("🔑 Mot de passe MarsPro: ").strip()
    
    if not email or not password:
        print("❌ Email et mot de passe requis")
        return
    
    tester = MarsPro_ExactFormat_Tester(email, password)
    
    try:
        # 1. Login
        print(f"\n🔐 Connexion...")
        if not await tester.login():
            print("❌ Échec de la connexion")
            return
        
        # 2. Récupérer les appareils
        print(f"\n📱 Récupération des appareils...")
        devices = await tester.get_device_list()
        
        if not devices:
            print("❌ Aucun appareil trouvé")
            return
        
        # 3. Afficher les appareils disponibles
        print(f"\n📋 Appareils disponibles:")
        for i, device in enumerate(devices):
            name = device.get('deviceName', 'N/A')
            serial = device.get('deviceSerialnum', 'N/A')
            status = 'ON' if not device.get('isClose', False) else 'OFF'
            print(f"   {i+1}. {name} ({serial}) - {status}")
        
        # 4. Test de contrôle avec le premier appareil
        device = devices[0]
        device_serial = device.get('deviceSerialnum')
        
        if device_serial:
            print(f"\n🎛️  Test de contrôle avec {device.get('deviceName', 'Appareil')}...")
            
            # Test différentes luminosités
            for brightness in [30, 60, 100]:
                print(f"\n--- Test luminosité {brightness}% ---")
                success = await tester.test_exact_control_format(device_serial, brightness)
                if success:
                    print(f"✅ Luminosité {brightness}% appliquée !")
                    await asyncio.sleep(2)  # Pause entre les tests
                else:
                    print(f"❌ Échec luminosité {brightness}%")
                    break
            
            print(f"\n🎉 Tests terminés !")
        else:
            print("❌ Pas de numéro de série trouvé pour l'appareil")
    
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 