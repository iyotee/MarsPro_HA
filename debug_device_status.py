#!/usr/bin/env python3
"""
🔍 DEBUG STATUT APPAREIL ACTUEL
Vérifier l'ID/PID actuel et tester le contrôle direct
"""

import asyncio
import aiohttp
import json
import time
import random
import re

class DeviceStatusDebugger:
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
    
    async def get_current_device_status(self):
        """Récupérer le statut actuel complet de l'appareil"""
        
        print(f"\n🔍 STATUT ACTUEL DE L'APPAREIL")
        print("=" * 50)
        
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
        
        # Récupérer l'appareil du groupe 1
        payload = {
            "currentPage": 1,
            "type": None,
            "deviceProductGroup": 1
        }
        
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/api/android/udm/getDeviceList/v1"
            async with session.post(url, json=payload, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('code') == '000':
                        devices = data.get('data', {}).get('list', [])
                        
                        if devices:
                            device = devices[0]  # Premier appareil
                            
                            print(f"📱 APPAREIL TROUVÉ:")
                            print(f"   Nom: {device.get('deviceName')}")
                            print(f"   ID: {device.get('id')} ⭐ (ID ACTUEL !)")
                            print(f"   PID original: {device.get('devicePid', 'N/A')}")
                            print(f"   Serial: {device.get('deviceSerialnum', 'N/A')}")
                            
                            # Extraire PID du nom
                            name = device.get('deviceName', '')
                            pid_match = re.search(r'([A-F0-9]{12})$', name)
                            extracted_pid = pid_match.group(1) if pid_match else None
                            
                            print(f"   PID extrait: {extracted_pid} ⭐ (PID RÉEL !)")
                            print(f"   Online: {device.get('isOnline')}")
                            print(f"   Net Device: {device.get('isNetDevice')}")
                            print(f"   Device Mode: {device.get('deviceMode')}")
                            print(f"   Device Type: {device.get('deviceType')}")
                            
                            # Récupérer plus de détails
                            await self.get_device_details(device.get('id'))
                            
                            return device, extracted_pid
                        else:
                            print("❌ Aucun appareil trouvé")
                            return None, None
                    else:
                        print(f"❌ Erreur API: {data}")
                        return None, None
                else:
                    print(f"❌ HTTP Error: {response.status}")
                    return None, None
    
    async def get_device_details(self, device_id):
        """Récupérer les détails complets d'un appareil"""
        
        print(f"\n📋 DÉTAILS COMPLETS DE L'APPAREIL (ID: {device_id})")
        print("-" * 50)
        
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
            "deviceId": device_id
        }
        
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/api/android/udm/getDeviceDetail/v1"
            async with session.post(url, json=payload, headers=headers) as response:
                if response.status == 200:
                    try:
                        data = await response.json()
                        print(f"✅ Détails reçus:")
                        print(json.dumps(data, indent=2, ensure_ascii=False))
                        
                        # Analyser les capacités de l'appareil
                        if data.get('code') == '000' and data.get('data'):
                            device_data = data['data']
                            
                            # Déterminer le type d'appareil
                            device_name = device_data.get('deviceName', '').lower()
                            device_type = device_data.get('deviceType', '').lower()
                            
                            if 'fan' in device_name or 'fan' in device_type:
                                print(f"🌀 Type détecté: VENTILATEUR")
                            elif 'light' in device_name or 'lamp' in device_name or 'dimbox' in device_name:
                                print(f"💡 Type détecté: LUMIÈRE")
                            else:
                                print(f"❓ Type indéterminé")
                                
                            # Vérifier les fonctionnalités disponibles
                            functions = device_data.get('functions', [])
                            if functions:
                                print(f"🔧 Fonctionnalités disponibles:")
                                for func in functions:
                                    print(f"   - {func}")
                                    
                        return data
                        
                    except Exception as e:
                        print(f"❌ Erreur parsing détails: {e}")
                        return None
                else:
                    print(f"❌ HTTP Error détails: {response.status}")
                    return None
    
    async def test_control_with_current_data(self, device, extracted_pid):
        """Tester le contrôle avec les données actuelles"""
        
        if not device or not extracted_pid:
            print("❌ Pas de données d'appareil à tester")
            return
        
        print(f"\n🎛️  TEST CONTRÔLE AVEC DONNÉES ACTUELLES")
        print("=" * 60)
        
        device_id = device.get('id')
        device_name = device.get('deviceName')
        
        print(f"📱 Appareil: {device_name}")
        print(f"🆔 ID actuel: {device_id}")
        print(f"🎯 PID à utiliser: {extracted_pid}")
        
        # Test 1: Contrôle luminosité avec PID extrait
        print(f"\n🧪 TEST 1: Contrôle luminosité (PID: {extracted_pid})")
        result1 = await self.test_brightness_control(extracted_pid, 75)
        
        # Test 2: Contrôle avec ID comme PID
        print(f"\n🧪 TEST 2: Contrôle avec ID comme PID ({device_id})")
        result2 = await self.test_brightness_control(str(device_id), 75)
        
        # Test 3: Contrôle ON/OFF
        print(f"\n🧪 TEST 3: Switch ON/OFF")
        result3_off = await self.test_switch_control(extracted_pid, False)
        await asyncio.sleep(2)
        result3_on = await self.test_switch_control(extracted_pid, True)
        
        # Résumé
        print(f"\n📊 RÉSUMÉ DES TESTS")
        print("=" * 40)
        print(f"✅ Luminosité (PID): {'SUCCÈS' if result1 else 'ÉCHEC'}")
        print(f"✅ Luminosité (ID): {'SUCCÈS' if result2 else 'ÉCHEC'}")
        print(f"✅ Switch OFF: {'SUCCÈS' if result3_off else 'ÉCHEC'}")
        print(f"✅ Switch ON: {'SUCCÈS' if result3_on else 'ÉCHEC'}")
        
        if any([result1, result2, result3_off, result3_on]):
            print(f"\n🎉 AU MOINS UN CONTRÔLE FONCTIONNE !")
            print(f"💡 Votre lampe a-t-elle réagi à l'un des tests ?")
            print(f"📝 PID à utiliser dans HA: {extracted_pid}")
            print(f"📝 ID actuel: {device_id}")
        else:
            print(f"\n❌ AUCUN CONTRÔLE NE FONCTIONNE")
            print(f"🔍 L'appareil est peut-être en mode veille ou déconnecté")
    
    async def test_brightness_control(self, pid, brightness):
        """Tester le contrôle de luminosité"""
        
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
        
        inner_data = {
            "method": "outletCtrl",
            "params": {
                "pid": str(pid),
                "num": 0,
                "on": 1,
                "pwm": int(brightness)
            }
        }
        
        payload = {"data": json.dumps(inner_data)}
        
        print(f"   📤 Test luminosité {brightness}% avec PID: {pid}")
        
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/api/upData/device"
            async with session.post(url, json=payload, headers=headers) as response:
                if response.status == 200:
                    try:
                        response_data = await response.json()
                        success = response_data.get('code') == '000'
                        
                        if success:
                            print(f"   ✅ Succès ! Code: {response_data.get('code')}")
                        else:
                            print(f"   ❌ Échec. Code: {response_data.get('code')}, Msg: {response_data.get('msg')}")
                        
                        return success
                    except Exception as e:
                        print(f"   ❌ Erreur parsing: {e}")
                        return False
                else:
                    print(f"   ❌ HTTP Error: {response.status}")
                    return False
    
    async def test_switch_control(self, pid, is_on):
        """Tester le contrôle ON/OFF"""
        
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
        
        inner_data = {
            "method": "outletCtrl",
            "params": {
                "pid": str(pid),
                "num": 0,
                "on": 1 if is_on else 0,
                "pwm": 100 if is_on else 0
            }
        }
        
        payload = {"data": json.dumps(inner_data)}
        
        print(f"   📤 Test switch {'ON' if is_on else 'OFF'} avec PID: {pid}")
        
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/api/upData/device"
            async with session.post(url, json=payload, headers=headers) as response:
                if response.status == 200:
                    try:
                        response_data = await response.json()
                        success = response_data.get('code') == '000'
                        
                        if success:
                            print(f"   ✅ Succès ! Code: {response_data.get('code')}")
                        else:
                            print(f"   ❌ Échec. Code: {response_data.get('code')}, Msg: {response_data.get('msg')}")
                        
                        return success
                    except Exception as e:
                        print(f"   ❌ Erreur parsing: {e}")
                        return False
                else:
                    print(f"   ❌ HTTP Error: {response.status}")
                    return False

async def main():
    """Debug principal du statut de l'appareil"""
    print("🔍 DEBUG STATUT APPAREIL - RÉSOLUTION PROBLÈME HA")
    print("=" * 60)
    
    # Utiliser directement les bonnes credentials
    email = "jeremy.noverraz2@proton.me"
    password = "T00rT00r"
    
    print(f"📧 Email: {email}")
    print(f"🔑 Mot de passe: {'*' * len(password)}")
    
    debugger = DeviceStatusDebugger(email, password)
    
    try:
        # 1. Login
        if not await debugger.login():
            print("❌ Échec du login")
            return
        
        # 2. Récupérer le statut actuel
        device, extracted_pid = await debugger.get_current_device_status()
        
        if device and extracted_pid:
            # 3. Tester le contrôle
            await debugger.test_control_with_current_data(device, extracted_pid)
            
            # 4. Recommandations pour Home Assistant
            print(f"\n💡 RECOMMANDATIONS POUR CORRIGER HOME ASSISTANT")
            print("=" * 60)
            print(f"🔧 Problème identifié:")
            print(f"   - L'ID de l'appareil change : {device.get('id')}")
            print(f"   - Le PID reste stable : {extracted_pid}")
            print(f"   - HA doit utiliser le PID, pas l'ID")
            print()
            print(f"🛠️  Solution:")
            print(f"   1. Redémarrer l'intégration MarsPro dans HA")
            print(f"   2. Vérifier que l'API utilise le PID extrait")
            print(f"   3. S'assurer que le type d'appareil est 'LIGHT' pas 'FAN'")
            print()
            print(f"📝 Valeurs à utiliser:")
            print(f"   - PID stable: {extracted_pid}")
            print(f"   - ID actuel: {device.get('id')} (peut changer)")
            print(f"   - Nom: {device.get('deviceName')}")
        else:
            print("❌ Impossible de récupérer les données de l'appareil")
        
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 