#!/usr/bin/env python3
"""
🔍 TEST ENDPOINTS DE CONTRÔLE - Basé sur captures HTTP Toolkit
Teste différents endpoints possibles pour le contrôle
"""

import asyncio
import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'custom_components', 'marshydro'))

from api_marspro import MarsProAPI

class AdvancedMarsProTester(MarsProAPI):
    """Version étendue pour tester différents endpoints"""
    
    async def test_control_endpoint_1(self, brightness):
        """Test endpoint: /api/upData/device (actuel)"""
        await self._ensure_token()
        
        inner_data = {
            "method": "outletCtrl",
            "params": {
                "pid": self.device_serial,
                "num": 0,
                "on": 1,
                "pwm": int(brightness)
            }
        }
        
        payload = {"data": json.dumps(inner_data)}
        endpoint = "/api/upData/device"
        
        print(f"🔍 Test endpoint 1: {endpoint}")
        print(f"📝 Payload: {json.dumps(payload, indent=2)}")
        
        data = await self._make_request(endpoint, payload)
        print(f"📤 Réponse: {json.dumps(data, indent=2) if data else 'None'}")
        return data
    
    async def test_control_endpoint_2(self, brightness):
        """Test endpoint: /api/android/dua/upDataDevice/v1 (hypothèse basée sur captures)"""
        await self._ensure_token()
        
        # Format basé sur les captures
        payload = {
            "deviceSerialnum": self.device_serial,
            "data": json.dumps({
                "method": "outletCtrl",
                "params": {
                    "pid": self.device_serial,
                    "num": 0,
                    "on": 1,
                    "pwm": int(brightness)
                }
            })
        }
        
        endpoint = "/api/android/dua/upDataDevice/v1"
        
        print(f"🔍 Test endpoint 2: {endpoint}")
        print(f"📝 Payload: {json.dumps(payload, indent=2)}")
        
        data = await self._make_request(endpoint, payload)
        print(f"📤 Réponse: {json.dumps(data, indent=2) if data else 'None'}")
        return data
        
    async def test_control_endpoint_3(self, brightness):
        """Test endpoint: /api/android/udm/deviceControl/v1 (hypothèse)"""
        await self._ensure_token()
        
        payload = {
            "deviceId": self.device_id,
            "controlData": {
                "method": "outletCtrl",
                "params": {
                    "pid": self.device_serial,
                    "num": 0,
                    "on": 1,
                    "pwm": int(brightness)
                }
            }
        }
        
        endpoint = "/api/android/udm/deviceControl/v1"
        
        print(f"🔍 Test endpoint 3: {endpoint}")
        print(f"📝 Payload: {json.dumps(payload, indent=2)}")
        
        data = await self._make_request(endpoint, payload)
        print(f"📤 Réponse: {json.dumps(data, indent=2) if data else 'None'}")
        return data
        
    async def test_control_endpoint_4(self, brightness):
        """Test format simple avec deviceId uniquement"""
        await self._ensure_token()
        
        payload = {
            "deviceId": self.device_id,
            "brightness": brightness,
            "isOn": True
        }
        
        endpoint = "/api/upData/device"
        
        print(f"🔍 Test endpoint 4: {endpoint} (format simple)")
        print(f"📝 Payload: {json.dumps(payload, indent=2)}")
        
        data = await self._make_request(endpoint, payload)
        print(f"📤 Réponse: {json.dumps(data, indent=2) if data else 'None'}")
        return data

async def main():
    print("🔍 TEST DÉCOUVERTE ENDPOINTS DE CONTRÔLE")
    print("=" * 50)
    
    email = "jeremy.noverraz2@proton.me"
    password = "T00rT00r"
    
    try:
        tester = AdvancedMarsProTester(email, password)
        
        # Connexion
        await tester.login()
        print("✅ Connexion réussie\n")
        
        # Récupérer l'appareil
        light_data = await tester.get_lightdata()
        if not light_data:
            print("❌ Aucun appareil trouvé")
            return
            
        print(f"📱 Appareil: {light_data['deviceName']}")
        print(f"🆔 Device ID: {light_data['id']}")
        print(f"🔢 Serial (PID): {light_data['deviceSerialnum']}")
        print(f"💡 Luminosité actuelle: {light_data['deviceLightRate']}")
        print()
        
        # Test tous les endpoints possibles
        test_brightness = 50
        
        print("🧪 TEST 1: Endpoint actuel")
        print("-" * 30)
        result1 = await tester.test_control_endpoint_1(test_brightness)
        print()
        
        print("🧪 TEST 2: Endpoint Android DUA")
        print("-" * 30)
        result2 = await tester.test_control_endpoint_2(test_brightness)
        print()
        
        print("🧪 TEST 3: Endpoint Android UDM")
        print("-" * 30)
        result3 = await tester.test_control_endpoint_3(test_brightness)
        print()
        
        print("🧪 TEST 4: Format simple")
        print("-" * 30)
        result4 = await tester.test_control_endpoint_4(test_brightness)
        print()
        
        # Résumé
        print("📊 RÉSUMÉ DES TESTS")
        print("=" * 30)
        
        tests = [
            ("Endpoint 1 (/api/upData/device)", result1),
            ("Endpoint 2 (android/dua)", result2),
            ("Endpoint 3 (android/udm)", result3),
            ("Endpoint 4 (format simple)", result4)
        ]
        
        for name, result in tests:
            if result and result.get("code") == "000":
                print(f"✅ {name}: SUCCÈS")
            elif result:
                print(f"⚠️  {name}: Échec - Code: {result.get('code')}, Msg: {result.get('msg')}")
            else:
                print(f"❌ {name}: Aucune réponse")
        
        print(f"\n👀 REGARDEZ VOTRE LAMPE - Est-ce qu'elle a changé ?")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 