#!/usr/bin/env python3
"""
📶 TEST APPAREIL WIFI/HYBRIDE
Test de détection et contrôle d'appareils WiFi MarsPro
"""

import asyncio
import sys
import os
import json
import aiohttp
import time
import random

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'custom_components', 'marshydro'))

from api_marspro import MarsProAPI

class WiFiHybridTester(MarsProAPI):
    """Testeur pour appareils Bluetooth connectés via WiFi"""
    
    async def test_endpoint_android_mine(self, brightness):
        """Test endpoint /api/android/mine/ pattern"""
        await self._ensure_token()
        
        payload = {
            "deviceId": self.device_id,
            "deviceSerialnum": self.device_serial,
            "brightness": int(brightness),
            "action": "setBrightness"
        }
        
        endpoint = "/api/android/mine/deviceControl/v1"
        
        print(f"🔍 Test endpoint MINE: {endpoint}")
        print(f"📝 Payload: {json.dumps(payload, indent=2)}")
        
        data = await self._make_request(endpoint, payload)
        print(f"📤 Réponse: {json.dumps(data, indent=2) if data else 'None'}")
        return data
        
    async def test_direct_device_command(self, brightness):
        """Test commande directe appareil"""
        await self._ensure_token()
        
        payload = {
            "deviceSerialnum": self.device_serial,
            "command": "setBrightness",
            "value": int(brightness)
        }
        
        endpoint = "/api/android/device/command/v1"
        
        print(f"🔍 Test commande directe: {endpoint}")
        print(f"📝 Payload: {json.dumps(payload, indent=2)}")
        
        data = await self._make_request(endpoint, payload)
        print(f"📤 Réponse: {json.dumps(data, indent=2) if data else 'None'}")
        return data
        
    async def test_wifi_control(self, brightness):
        """Test contrôle WiFi spécifique"""
        await self._ensure_token()
        
        inner_data = {
            "method": "wifiCtrl",
            "params": {
                "deviceSerialnum": self.device_serial,
                "brightness": int(brightness),
                "isOn": True
            }
        }
        
        payload = {"data": json.dumps(inner_data)}
        endpoint = "/api/upData/device"
        
        print(f"🌐 Test contrôle WiFi: {endpoint}")
        print(f"📝 Payload: {json.dumps(payload, indent=2)}")
        
        data = await self._make_request(endpoint, payload)
        print(f"📤 Réponse: {json.dumps(data, indent=2) if data else 'None'}")
        return data
        
    async def test_outlet_wifi_mode(self, brightness):
        """Test outletCtrl avec mode WiFi"""
        await self._ensure_token()
        
        inner_data = {
            "method": "outletCtrl",
            "params": {
                "pid": self.device_serial,
                "num": 0,
                "on": 1,
                "pwm": int(brightness),
                "connectionType": "wifi",
                "deviceType": "hybrid"
            }
        }
        
        payload = {"data": json.dumps(inner_data)}
        endpoint = "/api/upData/device"
        
        print(f"🔗 Test outletCtrl WiFi: {endpoint}")
        print(f"📝 Payload: {json.dumps(payload, indent=2)}")
        
        data = await self._make_request(endpoint, payload)
        print(f"📤 Réponse: {json.dumps(data, indent=2) if data else 'None'}")
        return data
        
    async def test_device_switch_wifi(self, is_on):
        """Test switch WiFi"""
        await self._ensure_token()
        
        inner_data = {
            "method": "deviceSwitch",
            "params": {
                "deviceId": self.device_id,
                "deviceSerialnum": self.device_serial,
                "isOn": is_on,
                "connectionType": "wifi"
            }
        }
        
        payload = {"data": json.dumps(inner_data)}
        endpoint = "/api/upData/device"
        
        print(f"🔘 Test switch WiFi ({'ON' if is_on else 'OFF'}): {endpoint}")
        print(f"📝 Payload: {json.dumps(payload, indent=2)}")
        
        data = await self._make_request(endpoint, payload)
        print(f"📤 Réponse: {json.dumps(data, indent=2) if data else 'None'}")
        return data

class MarsProWiFiDeviceDetector:
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
    
    async def test_correct_payload_from_captures(self):
        """Tester avec le payload EXACT des captures d'écran"""
        
        print(f"\n🎯 TEST AVEC PAYLOAD EXACT DES CAPTURES")
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
        
        # Payload EXACT de la capture 3
        print("\n📤 PAYLOAD EXACT DE LA CAPTURE (deviceProductGroup: 2)")
        payload_capture = {
            "currentPage": 1,
            "type": None,
            "deviceProductGroup": 2
        }
        
        await self.test_device_payload(headers, payload_capture, "Payload exact capture (WiFi/Hybride)")
        
        # Tester d'autres valeurs de deviceProductGroup
        print(f"\n🔍 TEST AUTRES VALEURS DE DEVICEPRODUCTGROUP")
        
        for group_id in [1, 3, 4, 5, None]:
            payload = {
                "currentPage": 1,
                "type": None,
                "deviceProductGroup": group_id
            }
            
            await self.test_device_payload(headers, payload, f"deviceProductGroup: {group_id}")
    
    async def test_device_payload(self, headers, payload, description):
        """Tester un payload spécifique"""
        
        print(f"\n   🔬 {description}")
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
                    
                    if status == 200 and isinstance(data, dict):
                        if data.get('code') == '000':
                            devices = data.get('data', {})
                            if isinstance(devices, dict):
                                device_list = devices.get('list', [])
                                print(f"   ✅ {len(device_list)} appareils trouvés !")
                                
                                for i, device in enumerate(device_list):
                                    device_id = device.get('id', 'N/A')
                                    device_name = device.get('deviceName', 'N/A')
                                    device_pid = device.get('devicePid', 'N/A')
                                    is_online = device.get('isOnline', 'N/A')
                                    is_net_device = device.get('isNetDevice', 'N/A')
                                    device_mode = device.get('deviceMode', 'N/A')
                                    
                                    print(f"      📱 {i+1}. {device_name}")
                                    print(f"         ID: {device_id}")
                                    print(f"         PID: {device_pid}")
                                    print(f"         Online: {is_online}")
                                    print(f"         Net Device: {is_net_device}")
                                    print(f"         Mode: {device_mode}")
                                    print()
                                
                                if device_list:
                                    return device_list
                            else:
                                print(f"   ⚠️  Data format inattendu: {type(devices)}")
                        else:
                            print(f"   ❌ Code erreur: {data.get('code')} - {data.get('msg')}")
                    else:
                        print(f"   ❌ HTTP {status}")
                        
            except Exception as e:
                print(f"   ❌ Exception: {e}")
        
        return []
    
    async def test_device_control_with_found_devices(self, devices):
        """Tester le contrôle avec les appareils trouvés"""
        
        if not devices:
            print("❌ Aucun appareil à tester")
            return
        
        print(f"\n🎛️  TEST CONTRÔLE DES APPAREILS TROUVÉS")
        print("=" * 60)
        
        for i, device in enumerate(devices):
            device_id = device.get('id')
            device_name = device.get('deviceName', f'Appareil {i+1}')
            device_pid = device.get('devicePid')
            
            print(f"\n📱 Test {device_name} (ID: {device_id})")
            
            # Si on a un PID, essayer le contrôle direct
            if device_pid and device_pid != 'N/A' and device_pid:
                print(f"   🎯 Test contrôle avec PID: {device_pid}")
                
                # Test avec format outletCtrl
                await self.test_outlet_control(device_pid, 50)
            else:
                print(f"   ⚠️  Pas de PID disponible pour le contrôle")
                print(f"   💡 ID appareil: {device_id} - peut nécessiter un autre endpoint")
    
    async def test_outlet_control(self, device_pid, pwm_value):
        """Test de contrôle avec format outletCtrl"""
        
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
        
        # Format outletCtrl
        inner_data = {
            "method": "outletCtrl",
            "params": {
                "pid": device_pid,
                "num": 0,
                "on": 1,
                "pwm": pwm_value
            }
        }
        
        payload = {"data": json.dumps(inner_data)}
        
        print(f"   📤 Payload contrôle: {json.dumps(payload, indent=2)}")
        
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/api/upData/device"
            async with session.post(url, json=payload, headers=headers) as response:
                status = response.status
                
                try:
                    response_data = await response.json()
                except:
                    response_data = await response.text()
                
                print(f"   📥 Contrôle Status: {status}")
                print(f"   📥 Réponse: {response_data}")
                
                if status == 200 and isinstance(response_data, dict) and response_data.get('code') == '000':
                    print(f"   ✅ CONTRÔLE RÉUSSI avec PID WiFi/Hybride !")
                    return True
                else:
                    print(f"   ❌ Contrôle échoué")
                    return False

async def test_wifi_device():
    """Test spécifique pour appareils WiFi/Hybrides"""
    print("📶 TEST APPAREIL WIFI/HYBRIDE")
    print("=" * 50)
    print("🎯 Détection et contrôle d'appareils connectés WiFi")
    print()
    
    email = "jeremy.noverraz2@proton.me"
    password = "T00rT00r"
    
    try:
        # Connexion API
        print("🔧 Connexion à l'API MarsPro...")
        api = MarsProAPI(email, password)
        await api.login()
        print("✅ Connecté à l'API MarsPro")
        
        # Récupération de TOUS les appareils
        print("\n📱 Recherche de tous les appareils...")
        all_devices = await api.get_all_devices()
        
        if not all_devices:
            print("❌ Aucun appareil trouvé")
            return False
        
        print(f"✅ {len(all_devices)} appareil(s) trouvé(s)")
        print()
        
        # Analyser chaque appareil
        wifi_devices = []
        bluetooth_devices = []
        
        for i, device in enumerate(all_devices, 1):
            device_name = device.get("deviceName", "N/A")
            device_id = device.get("id", "N/A")
            is_online = device.get("isOnline", False)
            is_net_device = device.get("isNetDevice", False)
            connection_type = device.get("connection_type", "Unknown")
            stable_pid = (device.get("extracted_pid") or 
                         device.get("deviceSerialnum") or 
                         device.get("devicePid"))
            
            print(f"📱 Appareil {i}: {device_name}")
            print(f"   ID: {device_id}")
            print(f"   PID: {stable_pid}")
            print(f"   En ligne: {is_online}")
            print(f"   Appareil réseau: {is_net_device}")
            print(f"   Type connexion: {connection_type}")
            
            if connection_type == "WiFi" or is_net_device:
                wifi_devices.append(device)
                print(f"   ✅ → Appareil WiFi détecté !")
            else:
                bluetooth_devices.append(device)
                print(f"   🔵 → Appareil Bluetooth seul")
            
            print()
        
        # Tests spécifiques selon le type
        if wifi_devices:
            print("📶 TESTS APPAREILS WIFI:")
            print("-" * 40)
            
            for device in wifi_devices:
                device_name = device.get("deviceName")
                device_id = device.get("id")
                stable_pid = (device.get("extracted_pid") or 
                             device.get("deviceSerialnum") or 
                             device.get("devicePid"))
                
                print(f"\n🎯 Test WiFi pour: {device_name}")
                
                # Test 1: Format WiFi avec ID
                print(f"📤 Test 1: Format WiFi avec device ID...")
                success = await test_wifi_control_by_id(api, device_id, 60)
                if success:
                    print(f"   ✅ SUCCÈS WiFi avec ID !")
                    return True
                else:
                    print(f"   ❌ Échec WiFi avec ID")
                
                # Test 2: Format hybride
                print(f"📤 Test 2: Format hybride...")
                success = await test_hybrid_control(api, device_id, stable_pid, 60)
                if success:
                    print(f"   ✅ SUCCÈS format hybride !")
                    return True
                else:
                    print(f"   ❌ Échec format hybride")
                
                await asyncio.sleep(2)
        
        if bluetooth_devices:
            print("🔵 APPAREILS BLUETOOTH SEULS DÉTECTÉS:")
            print("-" * 40)
            for device in bluetooth_devices:
                device_name = device.get("deviceName")
                print(f"📱 {device_name}")
            print(f"⚠️  Ces appareils nécessitent probablement une connexion WiFi")
            print(f"   pour recevoir les commandes de l'API cloud !")
        
        print("\n" + "=" * 50)
        print("🏁 ANALYSE TERMINÉE")
        print()
        print("📊 RÉSULTATS:")
        print(f"   📶 Appareils WiFi: {len(wifi_devices)}")
        print(f"   🔵 Appareils Bluetooth: {len(bluetooth_devices)}")
        print()
        print("💡 RECOMMANDATION:")
        if wifi_devices:
            print("   ✅ Appareils WiFi trouvés - contrôle possible")
        else:
            print("   ⚠️  Connectez vos appareils au WiFi pour le contrôle cloud")
        
        return len(wifi_devices) > 0
        
    except Exception as e:
        print(f"❌ Erreur dans le test: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_wifi_control_by_id(api, device_id, brightness):
    """Test contrôle WiFi avec device ID"""
    try:
        # Format WiFi spécifique
        inner_data = {
            "method": "wifiControl",
            "params": {
                "deviceId": str(device_id),
                "brightness": int(brightness),
                "power": 1
            }
        }
        
        payload = {"data": json.dumps(inner_data)}
        endpoint = api.endpoints["device_control"]
        
        data = await api._make_request(endpoint, payload)
        
        if data and data.get('code') == '000':
            print(f"      ✅ Commande WiFi réussie")
            await asyncio.sleep(3)  # Attendre pour voir l'effet
            return True
        else:
            print(f"      ❌ Commande WiFi échouée: {data}")
            return False
            
    except Exception as e:
        print(f"      ❌ Exception WiFi: {e}")
        return False

async def test_hybrid_control(api, device_id, pid, brightness):
    """Test contrôle hybride (WiFi + Bluetooth data)"""
    try:
        # Format hybride
        inner_data = {
            "method": "hybridControl",
            "params": {
                "deviceId": str(device_id),
                "pid": str(pid),
                "brightness": int(brightness),
                "power": 1,
                "type": "wifi"
            }
        }
        
        payload = {"data": json.dumps(inner_data)}
        endpoint = api.endpoints["device_control"]
        
        data = await api._make_request(endpoint, payload)
        
        if data and data.get('code') == '000':
            print(f"      ✅ Commande hybride réussie")
            await asyncio.sleep(3)
            return True
        else:
            print(f"      ❌ Commande hybride échouée: {data}")
            return False
            
    except Exception as e:
        print(f"      ❌ Exception hybride: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_wifi_device()) 