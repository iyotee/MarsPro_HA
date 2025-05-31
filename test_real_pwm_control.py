#!/usr/bin/env python3
"""
Test du contrôle PWM avec l'appareil réel trouvé
MH-DIMBOX-345F45EC73CC (ID: 129228)
"""

import asyncio
import aiohttp
import json
import time
import random
import re

class RealDevicePWMTester:
    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.token = None
        self.user_id = None
        self.base_url = "https://mars-pro.api.lgledsolutions.com"
        self.found_devices = []
        
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
    
    async def get_real_devices(self):
        """Récupérer les appareils réels avec deviceProductGroup: 1"""
        
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
        
        # Payload correct pour appareils Bluetooth
        payload = {
            "currentPage": 1,
            "type": None,
            "deviceProductGroup": 1
        }
        
        print(f"\n📱 Récupération des appareils réels...")
        
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/api/android/udm/getDeviceList/v1"
            async with session.post(url, json=payload, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('code') == '000':
                        devices = data.get('data', {}).get('list', [])
                        
                        print(f"✅ Trouvé {len(devices)} appareils")
                        
                        for i, device in enumerate(devices):
                            name = device.get('deviceName', 'N/A')
                            device_id = device.get('id', 'N/A')
                            pid = device.get('devicePid', 'N/A') or device.get('deviceSerialnum', 'N/A')
                            
                            # Extraire PID du nom si nécessaire
                            extracted_pid = None
                            if pid == 'N/A' or not pid:
                                pid_match = re.search(r'([A-F0-9]{12})$', name)
                                if pid_match:
                                    extracted_pid = pid_match.group(1)
                            
                            device['extracted_pid'] = extracted_pid
                            
                            print(f"   {i+1}. {name}")
                            print(f"      ID: {device_id}")
                            print(f"      PID original: {pid}")
                            if extracted_pid:
                                print(f"      PID extrait: {extracted_pid}")
                        
                        self.found_devices = devices
                        return devices
                    else:
                        print(f"❌ Erreur API: {data}")
                        return []
                else:
                    print(f"❌ HTTP Error: {response.status}")
                    return []
    
    async def test_pwm_control_all_methods(self, device, pwm_values=[10, 30, 57, 80, 100]):
        """Tester le contrôle PWM avec toutes les méthodes possibles"""
        
        device_name = device.get('deviceName', 'Appareil')
        device_id = device.get('id')
        original_pid = device.get('devicePid') or device.get('deviceSerialnum')
        extracted_pid = device.get('extracted_pid')
        
        print(f"\n🎛️  TEST CONTRÔLE PWM - {device_name}")
        print("=" * 60)
        print(f"Device ID: {device_id}")
        print(f"PID original: {original_pid}")
        print(f"PID extrait: {extracted_pid}")
        
        # Tester avec tous les PIDs possibles
        test_pids = []
        if extracted_pid:
            test_pids.append(extracted_pid)
        if original_pid and original_pid != 'N/A':
            test_pids.append(original_pid)
        test_pids.append(str(device_id))  # ID comme fallback
        
        # Supprimer les doublons en gardant l'ordre
        test_pids = list(dict.fromkeys(test_pids))
        
        print(f"\n🎯 PIDs à tester: {test_pids}")
        
        for pid in test_pids:
            print(f"\n--- Test avec PID: {pid} ---")
            
            success = False
            for pwm in pwm_values:
                print(f"📶 Test PWM {pwm}% avec PID {pid}...")
                
                result = await self.test_outlet_control(pid, pwm)
                if result:
                    print(f"✅ PWM {pwm}% réussi avec PID {pid} !")
                    success = True
                    await asyncio.sleep(2)  # Pause pour voir l'effet
                else:
                    print(f"❌ PWM {pwm}% échoué avec PID {pid}")
                    break
            
            if success:
                print(f"🎉 CONTRÔLE RÉUSSI AVEC PID: {pid}")
                return True, pid
            else:
                print(f"❌ Aucun contrôle réussi avec PID: {pid}")
        
        print(f"❌ Aucun PID ne fonctionne pour le contrôle")
        return False, None
    
    async def test_outlet_control(self, pid, pwm_value):
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
        
        # Format outletCtrl standard
        inner_data = {
            "method": "outletCtrl",
            "params": {
                "pid": str(pid),
                "num": 0,
                "on": 1,
                "pwm": int(pwm_value)
            }
        }
        
        payload = {"data": json.dumps(inner_data)}
        
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/api/upData/device"
            async with session.post(url, json=payload, headers=headers) as response:
                status = response.status
                
                try:
                    response_data = await response.json()
                except:
                    response_data = await response.text()
                
                if status == 200 and isinstance(response_data, dict) and response_data.get('code') == '000':
                    return True
                else:
                    return False

async def main():
    """Test principal avec votre appareil réel"""
    print("🚀 TEST CONTRÔLE PWM APPAREIL RÉEL")
    print("=" * 60)
    
    email = input("📧 Email MarsPro: ").strip()
    password = input("🔑 Mot de passe MarsPro: ").strip()
    
    if not email or not password:
        print("❌ Email et mot de passe requis")
        return
    
    tester = RealDevicePWMTester(email, password)
    
    try:
        # 1. Login
        if not await tester.login():
            print("❌ Échec du login")
            return
        
        # 2. Récupérer les appareils
        devices = await tester.get_real_devices()
        
        if not devices:
            print("❌ Aucun appareil trouvé")
            return
        
        # 3. Tester le contrôle sur chaque appareil
        for device in devices:
            success, working_pid = await tester.test_pwm_control_all_methods(device)
            
            if success:
                print(f"\n🎉 SUCCÈS TOTAL !")
                print(f"📱 Appareil: {device.get('deviceName')}")
                print(f"🎯 PID fonctionnel: {working_pid}")
                print(f"💡 Vous pouvez maintenant utiliser ce PID dans Home Assistant !")
                break
        else:
            print(f"\n❌ Aucun appareil n'a pu être contrôlé")
            print(f"💡 Vérifiez que vos appareils sont en mode Bluetooth")
        
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 