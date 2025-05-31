#!/usr/bin/env python3
"""
🔍 DÉCOUVERTE COMPLÈTE DES APPAREILS - Tous types WiFi/Bluetooth
Teste tous les deviceProductGroup pour trouver TOUS les appareils
"""

import asyncio
import aiohttp
import json
import time
import random
import re

class CompleteDeviceDiscovery:
    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.token = None
        self.user_id = None
        self.base_url = "https://mars-pro.api.lgledsolutions.com"
        self.all_devices = {}  # Groupé par deviceProductGroup
        
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
    
    async def discover_all_device_groups(self):
        """Découvrir tous les groupes d'appareils possibles"""
        
        print(f"\n🔍 DÉCOUVERTE COMPLÈTE DE TOUS LES GROUPES D'APPAREILS")
        print("=" * 70)
        
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
        
        # Tester tous les groupes d'appareils possibles
        device_groups_to_test = [
            (None, "Tous appareils (null)"),
            (1, "Groupe 1 (Bluetooth)"),
            (2, "Groupe 2 (WiFi)"),
            (3, "Groupe 3 (Hybride)"),
            (4, "Groupe 4 (Pro)"),
            (5, "Groupe 5 (Enterprise)"),
            (6, "Groupe 6 (IoT)"),
            (7, "Groupe 7 (Smart)"),
            (8, "Groupe 8 (Commercial)"),
            (9, "Groupe 9 (Industrial)"),
            (10, "Groupe 10 (Custom)")
        ]
        
        total_devices = 0
        
        for group_id, description in device_groups_to_test:
            print(f"\n📡 Test {description}")
            print("-" * 50)
            
            payload = {
                "currentPage": 1,
                "type": None,
                "deviceProductGroup": group_id
            }
            
            devices = await self.get_devices_for_group(headers, payload, group_id, description)
            
            if devices:
                self.all_devices[group_id] = devices
                total_devices += len(devices)
                print(f"✅ {len(devices)} appareils trouvés dans {description}")
                
                # Afficher détails de chaque appareil
                for i, device in enumerate(devices):
                    name = device.get('deviceName', 'N/A')
                    device_id = device.get('id', 'N/A')
                    pid = device.get('devicePid', 'N/A') or device.get('deviceSerialnum', 'N/A')
                    is_online = device.get('isOnline', 'N/A')
                    is_net_device = device.get('isNetDevice', False)
                    device_mode = device.get('deviceMode', 'N/A')
                    device_type = device.get('deviceType', 'N/A')
                    
                    # Extraire PID du nom si nécessaire
                    extracted_pid = None
                    if pid == 'N/A' or not pid:
                        pid_match = re.search(r'([A-F0-9]{12})$', name)
                        if pid_match:
                            extracted_pid = pid_match.group(1)
                    
                    print(f"   📱 {i+1}. {name}")
                    print(f"      ID: {device_id}")
                    print(f"      PID: {pid}")
                    if extracted_pid:
                        print(f"      PID extrait: {extracted_pid}")
                    print(f"      Online: {is_online}")
                    print(f"      Net Device: {is_net_device}")
                    print(f"      Mode: {device_mode}")
                    print(f"      Type: {device_type}")
                    print()
            else:
                print(f"❌ Aucun appareil dans {description}")
        
        print(f"\n📊 RÉSUMÉ DE LA DÉCOUVERTE")
        print("=" * 50)
        print(f"🔢 Total des appareils trouvés: {total_devices}")
        print(f"📁 Groupes avec appareils: {len(self.all_devices)}")
        
        # Analyser les types de connexion
        bluetooth_devices = []
        wifi_devices = []
        hybrid_devices = []
        
        for group_id, devices in self.all_devices.items():
            for device in devices:
                name = device.get('deviceName', '')
                is_net_device = device.get('isNetDevice', False)
                device_mode = device.get('deviceMode', '')
                
                if is_net_device or 'wifi' in name.lower() or 'net' in device_mode.lower():
                    wifi_devices.append((group_id, device))
                elif 'bluetooth' in name.lower() or 'bt' in name.lower():
                    bluetooth_devices.append((group_id, device))
                else:
                    # Supposer Bluetooth par défaut pour les appareils non-réseau
                    if not is_net_device:
                        bluetooth_devices.append((group_id, device))
                    else:
                        hybrid_devices.append((group_id, device))
        
        print(f"\n🔵 Appareils Bluetooth: {len(bluetooth_devices)}")
        for group_id, device in bluetooth_devices:
            print(f"   📱 {device.get('deviceName')} (Groupe {group_id})")
        
        print(f"\n🌐 Appareils WiFi: {len(wifi_devices)}")
        for group_id, device in wifi_devices:
            print(f"   📡 {device.get('deviceName')} (Groupe {group_id})")
        
        print(f"\n🔀 Appareils Hybrides: {len(hybrid_devices)}")
        for group_id, device in hybrid_devices:
            print(f"   🔄 {device.get('deviceName')} (Groupe {group_id})")
        
        return self.all_devices
    
    async def get_devices_for_group(self, headers, payload, group_id, description):
        """Récupérer les appareils pour un groupe spécifique"""
        
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/api/android/udm/getDeviceList/v1"
            
            try:
                async with session.post(url, json=payload, headers=headers, timeout=30) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get('code') == '000':
                            devices = data.get('data', {}).get('list', [])
                            return devices
                        else:
                            return []
                    else:
                        return []
            except Exception as e:
                print(f"   ❌ Erreur pour {description}: {e}")
                return []
    
    async def test_all_device_control(self):
        """Tester le contrôle sur tous les appareils trouvés"""
        
        if not self.all_devices:
            print("❌ Aucun appareil à tester")
            return
        
        print(f"\n🎛️  TEST DE CONTRÔLE SUR TOUS LES APPAREILS")
        print("=" * 60)
        
        successful_controls = []
        
        for group_id, devices in self.all_devices.items():
            print(f"\n📁 Test des appareils du Groupe {group_id}")
            print("-" * 40)
            
            for device in devices:
                name = device.get('deviceName', 'Appareil inconnu')
                device_id = device.get('id')
                pid = device.get('devicePid') or device.get('deviceSerialnum')
                
                # Extraire PID du nom si nécessaire
                extracted_pid = None
                if not pid or pid == 'N/A':
                    pid_match = re.search(r'([A-F0-9]{12})$', name)
                    if pid_match:
                        extracted_pid = pid_match.group(1)
                
                print(f"\n🧪 Test contrôle: {name}")
                
                # Tester avec différents PIDs
                test_pids = []
                if extracted_pid:
                    test_pids.append(extracted_pid)
                if pid and pid != 'N/A':
                    test_pids.append(pid)
                test_pids.append(str(device_id))
                
                # Supprimer doublons
                test_pids = list(dict.fromkeys(test_pids))
                
                for test_pid in test_pids:
                    result = await self.test_device_control(test_pid, 75)
                    
                    if result:
                        print(f"   ✅ CONTRÔLE RÉUSSI avec PID: {test_pid}")
                        successful_controls.append({
                            'group': group_id,
                            'device': device,
                            'working_pid': test_pid,
                            'name': name
                        })
                        break
                    else:
                        print(f"   ❌ Échec avec PID: {test_pid}")
                
                await asyncio.sleep(1)  # Pause entre tests
        
        # Résumé final
        print(f"\n🎉 RÉSUMÉ FINAL DU CONTRÔLE")
        print("=" * 50)
        
        if successful_controls:
            print(f"✅ {len(successful_controls)} appareils contrôlables trouvés !")
            
            for control in successful_controls:
                print(f"\n📱 {control['name']}")
                print(f"   🎯 PID fonctionnel: {control['working_pid']}")
                print(f"   📁 Groupe: {control['group']}")
                print(f"   💡 Type de connexion: {'WiFi' if control['device'].get('isNetDevice') else 'Bluetooth'}")
        else:
            print(f"❌ Aucun appareil contrôlable trouvé")
            print(f"💡 Vérifiez que vos appareils sont allumés et connectés")
        
        return successful_controls
    
    async def test_device_control(self, pid, pwm_value):
        """Tester le contrôle d'un appareil avec un PID"""
        
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
        
        # Test avec format outletCtrl (marche pour Bluetooth et certains WiFi)
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
                if response.status == 200:
                    try:
                        response_data = await response.json()
                        return response_data.get('code') == '000'
                    except:
                        return False
                else:
                    return False

async def main():
    """Test principal de découverte complète"""
    print("🌍 DÉCOUVERTE COMPLÈTE - TOUS APPAREILS WiFi/Bluetooth")
    print("=" * 70)
    
    email = input("📧 Email MarsPro: ").strip()
    password = input("🔑 Mot de passe MarsPro: ").strip()
    
    if not email or not password:
        print("❌ Email et mot de passe requis")
        return
    
    discovery = CompleteDeviceDiscovery(email, password)
    
    try:
        # 1. Login
        if not await discovery.login():
            print("❌ Échec du login")
            return
        
        # 2. Découverte complète
        all_devices = await discovery.discover_all_device_groups()
        
        if not all_devices:
            print("❌ Aucun appareil trouvé dans aucun groupe")
            return
        
        # 3. Test de contrôle sur tous les appareils
        working_devices = await discovery.test_all_device_control()
        
        # 4. Recommandations finales
        print(f"\n💡 RECOMMANDATIONS POUR L'API HOME ASSISTANT")
        print("=" * 60)
        
        if working_devices:
            print(f"✅ Intégration possible avec {len(working_devices)} appareils")
            print(f"📝 Mettre à jour l'API pour inclure ces groupes:")
            
            groups_with_devices = set(device['group'] for device in working_devices)
            for group in sorted(groups_with_devices):
                device_count = len([d for d in working_devices if d['group'] == group])
                print(f"   - deviceProductGroup: {group} ({device_count} appareils)")
        else:
            print(f"❌ Aucun appareil contrôlable")
            print(f"💡 Essayez de connecter vos appareils via l'app MarsPro d'abord")
        
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 