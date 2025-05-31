#!/usr/bin/env python3
"""
Test du format outletCtrl avec récupération automatique des vrais PIDs
Format simple et fonctionnel pour MarsPro
"""

import asyncio
import aiohttp
import json
import time
import random

class MarsPro_OutletCtrl_Tester:
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
    
    async def get_real_devices(self):
        """Récupérer les vrais appareils du compte utilisateur"""
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
        
        print(f"\n📱 Récupération des appareils réels...")
        
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/api/android/udm/getDeviceList/v1"
            async with session.post(url, json=payload, headers=headers) as response:
                status = response.status
                
                try:
                    data = await response.json()
                except:
                    data = await response.text()
                
                if status == 200 and isinstance(data, dict):
                    if data.get('code') == '000':
                        devices = data.get('data', {}).get('list', [])
                        print(f"✅ Trouvé {len(devices)} appareils réels")
                        
                        # Afficher les appareils disponibles
                        for i, device in enumerate(devices):
                            name = device.get('deviceName', 'N/A')
                            pid = device.get('deviceSerialnum', 'N/A')
                            status_text = 'ON' if not device.get('isClose', False) else 'OFF'
                            device_type = device.get('productType', 'N/A')
                            print(f"   {i+1}. {name} (PID: {pid}) - {status_text} - Type: {device_type}")
                        
                        return devices
                    else:
                        print(f"❌ Erreur API: Code {data.get('code')} - {data.get('msg')}")
                        return []
                else:
                    print(f"❌ HTTP Error: {status}")
                    return []
    
    async def test_outletctrl_control(self, device_serial, pwm_value=57):
        """Test du format outletCtrl EXACT avec PID réel"""
        
        print(f"\n🎯 TEST FORMAT OUTLETCTRL AVEC PID RÉEL")
        print(f"Device PID: {device_serial}")
        print(f"PWM Value: {pwm_value}")
        
        # Format EXACT de la capture 3 !
        inner_data = {
            "method": "outletCtrl",  # Exactement comme dans capture 3
            "params": {
                "pid": device_serial,   # PID réel de l'utilisateur
                "num": 0,               # num: 0 exact de la capture
                "on": 1,                # on: 1 exact de la capture
                "pwm": pwm_value        # pwm: valeur variable
            }
        }
        
        # Le payload final doit être exactement comme dans la capture 3
        payload = {"data": json.dumps(inner_data)}
        
        print(f"\n📤 Payload envoyé (format outletCtrl avec PID réel):")
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
                    print(f"✅ CONTRÔLE RÉUSSI avec PID réel !")
                    return True
                else:
                    print(f"❌ Contrôle échoué")
                    return False

    async def test_different_pwm_values(self, device_serial):
        """Test avec différentes valeurs PWM sur appareil réel"""
        
        print(f"\n🎛️  TEST DIFFÉRENTES VALEURS PWM SUR APPAREIL RÉEL")
        
        # Valeurs PWM à tester
        pwm_values = [10, 30, 57, 80, 100]
        
        for pwm in pwm_values:
            print(f"\n--- Test PWM {pwm} sur {device_serial} ---")
            success = await self.test_outletctrl_control(device_serial, pwm)
            if success:
                print(f"✅ PWM {pwm} appliquée avec succès sur appareil réel !")
                await asyncio.sleep(3)  # Pause plus longue pour voir l'effet
            else:
                print(f"❌ Échec PWM {pwm}")
                break

async def main():
    """Test principal avec PIDs réels d'appareils"""
    print("🚀 TEST FORMAT OUTLETCTRL AVEC VRAIS PIDS MARSPRO")
    print("=" * 60)
    
    email = input("📧 Email MarsPro: ").strip()
    password = input("🔑 Mot de passe MarsPro: ").strip()
    
    if not email or not password:
        print("❌ Email et mot de passe requis")
        return
    
    tester = MarsPro_OutletCtrl_Tester(email, password)
    
    try:
        # 1. Login
        print(f"\n🔐 Connexion...")
        if not await tester.login():
            print("❌ Échec de la connexion")
            return
        
        # 2. Récupérer les vrais appareils
        devices = await tester.get_real_devices()
        
        if not devices:
            print("❌ Aucun appareil trouvé sur votre compte")
            return
        
        # 3. Sélectionner un appareil à tester
        if len(devices) == 1:
            selected_device = devices[0]
            print(f"\n🎯 Test automatique avec le seul appareil disponible")
        else:
            print(f"\n🔢 Choisissez un appareil à tester:")
            for i, device in enumerate(devices):
                name = device.get('deviceName', 'N/A')
                pid = device.get('deviceSerialnum', 'N/A')
                print(f"   {i+1}. {name} (PID: {pid})")
            
            try:
                choice = int(input("Numéro de l'appareil (1-{}): ".format(len(devices))).strip()) - 1
                if 0 <= choice < len(devices):
                    selected_device = devices[choice]
                else:
                    print("❌ Choix invalide")
                    return
            except ValueError:
                print("❌ Veuillez entrer un numéro valide")
                return
        
        device_name = selected_device.get('deviceName', 'Appareil')
        device_pid = selected_device.get('deviceSerialnum')
        
        if not device_pid:
            print("❌ PID de l'appareil non trouvé")
            return
        
        print(f"\n🎛️  Test de contrôle avec {device_name} (PID: {device_pid})...")
        
        # 4. Test de contrôle avec le PID réel
        success = await tester.test_outletctrl_control(device_pid, 57)
        
        if success:
            print(f"\n🎉 Format outletCtrl fonctionne avec votre appareil réel !")
            
            # Demander si on continue les tests
            continue_tests = input("\n🔄 Voulez-vous tester différentes valeurs PWM ? (y/N): ").strip().lower()
            if continue_tests in ['y', 'yes', 'oui', 'o']:
                await tester.test_different_pwm_values(device_pid)
            
            print(f"\n🎉 Tests terminés avec succès !")
        else:
            print(f"\n❌ Le contrôle a échoué avec votre appareil")
            print(f"💡 Vérifiez que l'appareil est en mode Bluetooth (pas WiFi)")
    
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 