#!/usr/bin/env python3
"""
🌐 TEST APPAREIL BLUETOOTH+WIFI - Nouveaux endpoints
Teste des appareils Bluetooth connectés via WiFi
"""

import asyncio
import sys
import os
import json

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

async def main():
    print("🌐 TEST APPAREIL BLUETOOTH+WIFI HYBRIDE")
    print("=" * 50)
    print("💡 Appareil Bluetooth connecté via réseau WiFi")
    print()
    
    email = "jeremy.noverraz2@proton.me"
    password = "T00rT00r"
    
    try:
        tester = WiFiHybridTester(email, password)
        
        # Connexion
        await tester.login()
        print("✅ Connexion réussie")
        
        # Récupérer l'appareil
        light_data = await tester.get_lightdata()
        if not light_data:
            print("❌ Aucun appareil trouvé")
            return False
            
        device_id = light_data['id']
        device_serial = light_data['deviceSerialnum']
        current_brightness = light_data['deviceLightRate']
        
        print(f"📱 Appareil: {light_data['deviceName']}")
        print(f"🆔 ID: {device_id}")
        print(f"🔢 Serial: {device_serial}")
        print(f"💡 Luminosité: {current_brightness}")
        print(f"🔗 Type: Bluetooth+WiFi Hybride")
        print()
        
        # Tests spécialisés pour WiFi
        test_brightness = 85
        
        print("🧪 TEST 1: Endpoint Android Mine")
        print("-" * 40)
        result1 = await tester.test_endpoint_android_mine(test_brightness)
        print("👀 REGARDEZ VOTRE LAMPE MAINTENANT !")
        await asyncio.sleep(5)
        print()
        
        print("🧪 TEST 2: Commande directe")
        print("-" * 40)
        result2 = await tester.test_direct_device_command(test_brightness)
        print("👀 REGARDEZ VOTRE LAMPE MAINTENANT !")
        await asyncio.sleep(5)
        print()
        
        print("🧪 TEST 3: Contrôle WiFi spécifique")
        print("-" * 40)
        result3 = await tester.test_wifi_control(test_brightness)
        print("👀 REGARDEZ VOTRE LAMPE MAINTENANT !")
        await asyncio.sleep(5)
        print()
        
        print("🧪 TEST 4: outletCtrl mode WiFi")
        print("-" * 40)
        result4 = await tester.test_outlet_wifi_mode(test_brightness)
        print("👀 REGARDEZ VOTRE LAMPE MAINTENANT !")
        await asyncio.sleep(5)
        print()
        
        print("🧪 TEST 5: Switch OFF WiFi")
        print("-" * 40)
        result5 = await tester.test_device_switch_wifi(False)
        print("👀 LA LAMPE DOIT S'ÉTEINDRE !")
        await asyncio.sleep(5)
        print()
        
        print("🧪 TEST 6: Switch ON WiFi")
        print("-" * 40)
        result6 = await tester.test_device_switch_wifi(True)
        print("👀 LA LAMPE DOIT SE RALLUMER !")
        await asyncio.sleep(5)
        print()
        
        # Résumé
        print("📊 RÉSUMÉ DES TESTS WIFI")
        print("=" * 40)
        
        tests = [
            ("Android Mine", result1),
            ("Commande directe", result2),
            ("Contrôle WiFi", result3),
            ("outletCtrl WiFi", result4),
            ("Switch OFF WiFi", result5),
            ("Switch ON WiFi", result6)
        ]
        
        working_tests = []
        for name, result in tests:
            if result and result.get("code") == "000":
                print(f"✅ {name}: SUCCÈS")
                working_tests.append(name)
            elif result:
                print(f"⚠️  {name}: Échec - Code: {result.get('code')}, Msg: {result.get('msg')}")
            else:
                print(f"❌ {name}: Aucune réponse")
        
        print(f"\n🎊 TESTS TERMINÉS !")
        print(f"❓ VOTRE LAMPE A-T-ELLE RÉAGI ?")
        
        if working_tests:
            print(f"✅ Tests techniques réussis: {', '.join(working_tests)}")
            print(f"💡 Si la lampe a réagi = PROBLÈME RÉSOLU !")
        else:
            print(f"⚠️  Tous les tests ont échoué techniquement")
            
        return True
        
    except Exception as e:
        print(f"❌ Erreur générale: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(main()) 