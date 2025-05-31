#!/usr/bin/env python3
"""
🎯 TEST CONTRÔLE RÉEL PWM - Nouveaux endpoints basés sur captures
"""

import asyncio
import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'custom_components', 'marshydro'))

from api_marspro import MarsProAPI

class NewEndpointTester(MarsProAPI):
    """Testeur avec les nouveaux endpoints des captures"""
    
    async def test_endpoint_android_mine(self, brightness):
        """Test endpoint /api/android/mine/ pattern"""
        await self._ensure_token()
        
        # Test avec le pattern mine/
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
        """Test commande directe sur l'appareil"""
        await self._ensure_token()
        
        # Format très simple pour appareil WiFi
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
        
    async def test_wifi_device_control(self, brightness):
        """Test contrôle spécifique WiFi"""
        await self._ensure_token()
        
        # Format pour appareil WiFi connecté
        inner_data = {
            "method": "wifiCtrl",  # Méthode WiFi au lieu de bluetoothCtrl
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
        
    async def test_hybrid_control(self, brightness):
        """Test format hybride Bluetooth+WiFi"""
        await self._ensure_token()
        
        inner_data = {
            "method": "hybridCtrl",
            "params": {
                "deviceId": self.device_id,
                "deviceSerialnum": self.device_serial,
                "connectionType": "wifi",  # Spécifier WiFi
                "brightness": int(brightness),
                "isOn": True
            }
        }
        
        payload = {"data": json.dumps(inner_data)}
        endpoint = "/api/upData/device"
        
        print(f"🔗 Test contrôle hybride: {endpoint}")
        print(f"📝 Payload: {json.dumps(payload, indent=2)}")
        
        data = await self._make_request(endpoint, payload)

async def test_pwm_control():
    """Test contrôle PWM avec formats des captures"""
    print("🔧 TEST CONTRÔLE PWM RÉEL")
    print("=" * 50)
    print("🎯 Basé sur les vraies captures HTTP Toolkit")
    print()
    
    email = "jeremy.noverraz2@proton.me"
    password = "T00rT00r"
    
    try:
        api = MarsProAPI(email, password)
        await api.login()
        print("✅ Connexion réussie")
        
        # Récupérer l'appareil
        light_data = await api.get_lightdata()
        device_serial = light_data['deviceSerialnum']
        
        print(f"📱 Appareil: {light_data['deviceName']}")
        print(f"🔢 Serial: {device_serial}")
        print(f"💡 Luminosité actuelle: {light_data['deviceLightRate']}")
        print(f"🔄 isStart: {light_data.get('isStart', 'unknown')}")
        print()
        
        print("🚨 FERMEZ L'APP MARSPRO SUR VOTRE TÉLÉPHONE MAINTENANT !")
        print("⏰ Attendez 10 secondes...")
        await asyncio.sleep(10)
        
        # Test 1: Format EXACT de votre capture avec PWM=59
        print("🧪 TEST 1: Format EXACT capture (PWM=59)")
        print("-" * 50)
        
        payload1 = {
            "data": json.dumps({
                "method": "outletCtrl",
                "params": {
                    "pid": device_serial,
                    "num": 0,
                    "on": 1,
                    "pwm": 59  # EXACT de votre capture !
                }
            })
        }
        
        print(f"📝 Payload: {json.dumps(payload1, indent=2)}")
        result1 = await api._make_request("/api/upData/device", payload1)
        print(f"📤 Réponse: {json.dumps(result1, indent=2) if result1 else 'None'}")
        print("👀 REGARDEZ LA LAMPE ! PWM=59")
        await asyncio.sleep(5)
        print()
        
        # Test 2: PWM=100 (maximum)
        print("🧪 TEST 2: PWM Maximum (100)")
        print("-" * 50)
        
        payload2 = {
            "data": json.dumps({
                "method": "outletCtrl",
                "params": {
                    "pid": device_serial,
                    "num": 0,
                    "on": 1,
                    "pwm": 100
                }
            })
        }
        
        print(f"📝 Payload: {json.dumps(payload2, indent=2)}")
        result2 = await api._make_request("/api/upData/device", payload2)
        print(f"📤 Réponse: {json.dumps(result2, indent=2) if result2 else 'None'}")
        print("👀 REGARDEZ LA LAMPE ! PWM=100 (MAX)")
        await asyncio.sleep(5)
        print()
        
        # Test 3: Éteindre (on=0)
        print("🧪 TEST 3: ÉTEINDRE (on=0)")
        print("-" * 50)
        
        payload3 = {
            "data": json.dumps({
                "method": "outletCtrl",
                "params": {
                    "pid": device_serial,
                    "num": 0,
                    "on": 0,
                    "pwm": 0
                }
            })
        }
        
        print(f"📝 Payload: {json.dumps(payload3, indent=2)}")
        result3 = await api._make_request("/api/upData/device", payload3)
        print(f"📤 Réponse: {json.dumps(result3, indent=2) if result3 else 'None'}")
        print("👀 LA LAMPE DOIT S'ÉTEINDRE MAINTENANT !")
        await asyncio.sleep(5)
        print()
        
        # Test 4: Rallumer PWM=50
        print("🧪 TEST 4: RALLUMER (PWM=50)")
        print("-" * 50)
        
        payload4 = {
            "data": json.dumps({
                "method": "outletCtrl",
                "params": {
                    "pid": device_serial,
                    "num": 0,
                    "on": 1,
                    "pwm": 50
                }
            })
        }
        
        print(f"📝 Payload: {json.dumps(payload4, indent=2)}")
        result4 = await api._make_request("/api/upData/device", payload4)
        print(f"📤 Réponse: {json.dumps(result4, indent=2) if result4 else 'None'}")
        print("👀 LA LAMPE DOIT SE RALLUMER À 50% !")
        await asyncio.sleep(5)
        print()
        
        # Vérifier l'état après les tests
        print("🔍 VÉRIFICATION ÉTAT FINAL")
        print("-" * 30)
        
        light_data_final = await api.get_lightdata()
        print(f"💡 Luminosité finale: {light_data_final['deviceLightRate']}")
        print(f"🔄 isStart final: {light_data_final.get('isStart', 'unknown')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

async def test_with_app_closed():
    """Test avec app fermée"""
    print("\n" + "="*60)
    print("🔒 TEST AVEC APP MARSPRO FERMÉE")
    print("="*60)
    
    print("📱 1. FERMEZ l'app MarsPro sur votre téléphone")
    print("⏰ 2. Attendez 30 secondes")
    print("🔧 3. On va tester les commandes")
    
    input("✋ Appuyez sur ENTRÉE quand l'app est fermée...")
    
    await test_pwm_control()

async def main():
    print("🚨 PROBLÈME DE CONFLIT CLOUD/LOCAL ?")
    print("=" * 50)
    print("🤔 L'app MarsPro bloque peut-être les commandes à distance")
    print()
    
    # D'abord tester l'état actuel
    print("💡 QUESTION: L'app MarsPro sur votre téléphone est-elle OUVERTE actuellement ?")
    response = input("📱 Tapez 'oui' si ouverte, 'non' si fermée: ").lower().strip()
    
    if response == 'oui':
        print("\n🔒 L'app est ouverte - cela peut bloquer les commandes à distance !")
        await test_with_app_closed()
    else:
        print("\n✅ App fermée - testons directement")
        await test_pwm_control()
    
    print(f"\n❓ RÉSULTAT: Est-ce que votre lampe a ENFIN bougé ?")

if __name__ == "__main__":
    asyncio.run(main()) 