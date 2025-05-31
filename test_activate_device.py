#!/usr/bin/env python3
"""
🚀 TEST ACTIVATION APPAREIL - Démarrer avant contrôler
"""

import asyncio
import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'custom_components', 'marshydro'))

from api_marspro import MarsProAPI

class DeviceActivationTester(MarsProAPI):
    """Testeur pour activer l'appareil avant contrôle"""
    
    async def test_device_activation(self):
        """Essayer différentes méthodes d'activation"""
        await self._ensure_token()
        
        activation_tests = []
        
        # Test 1: Activation par deviceSwitch
        print("🔌 Test 1: Activation deviceSwitch...")
        inner_data = {
            "method": "deviceSwitch",
            "params": {
                "deviceId": self.device_id,
                "deviceSerialnum": self.device_serial,
                "isOn": True
            }
        }
        payload = {"data": json.dumps(inner_data)}
        result1 = await self._make_request("/api/upData/device", payload)
        print(f"📤 Réponse: {json.dumps(result1, indent=2) if result1 else 'None'}")
        activation_tests.append(("deviceSwitch", result1))
        await asyncio.sleep(2)
        
        # Test 2: Commande start directe
        print("🚀 Test 2: Commande START...")
        inner_data = {
            "method": "start",
            "params": {
                "deviceId": self.device_id,
                "deviceSerialnum": self.device_serial
            }
        }
        payload = {"data": json.dumps(inner_data)}
        result2 = await self._make_request("/api/upData/device", payload)
        print(f"📤 Réponse: {json.dumps(result2, indent=2) if result2 else 'None'}")
        activation_tests.append(("start", result2))
        await asyncio.sleep(2)
        
        # Test 3: Activation avec enable
        print("✅ Test 3: Enable device...")
        inner_data = {
            "method": "enable",
            "params": {
                "deviceSerialnum": self.device_serial,
                "enable": True
            }
        }
        payload = {"data": json.dumps(inner_data)}
        result3 = await self._make_request("/api/upData/device", payload)
        print(f"📤 Réponse: {json.dumps(result3, indent=2) if result3 else 'None'}")
        activation_tests.append(("enable", result3))
        await asyncio.sleep(2)
        
        # Test 4: Power ON
        print("⚡ Test 4: Power ON...")
        inner_data = {
            "method": "power",
            "params": {
                "deviceSerialnum": self.device_serial,
                "power": "on"
            }
        }
        payload = {"data": json.dumps(inner_data)}
        result4 = await self._make_request("/api/upData/device", payload)
        print(f"📤 Réponse: {json.dumps(result4, indent=2) if result4 else 'None'}")
        activation_tests.append(("power", result4))
        await asyncio.sleep(2)
        
        # Test 5: Init device
        print("🔄 Test 5: Init device...")
        inner_data = {
            "method": "init",
            "params": {
                "deviceId": self.device_id,
                "deviceSerialnum": self.device_serial
            }
        }
        payload = {"data": json.dumps(inner_data)}
        result5 = await self._make_request("/api/upData/device", payload)
        print(f"📤 Réponse: {json.dumps(result5, indent=2) if result5 else 'None'}")
        activation_tests.append(("init", result5))
        
        return activation_tests
        
    async def check_device_status_after_activation(self):
        """Vérifier l'état après tentatives d'activation"""
        # Vérifier via getDeviceDetail
        payload = {"deviceId": self.device_id}
        endpoint = "/api/android/udm/getDeviceDetail/v1"
        
        data = await self._make_request(endpoint, payload)
        
        if data and data.get("code") == "000":
            device_data = data.get("data", {})
            
            print(f"\n📊 ÉTAT APRÈS ACTIVATION:")
            print(f"  🚀 isStart: {device_data.get('isStart')}")
            print(f"  🔌 isClose: {device_data.get('isClose')}")
            print(f"  💡 deviceLightRate: {device_data.get('deviceLightRate')}")
            print(f"  🌐 connectStatus: {device_data.get('connectStatus')}")
            
            return device_data.get('isStart') == 1  # Retourner si démarré
        
        return False

async def main():
    print("🚀 TEST ACTIVATION APPAREIL MZL001")
    print("=" * 50)
    print("💡 Tentative d'activation avant contrôle")
    print()
    
    email = "jeremy.noverraz2@proton.me"
    password = "T00rT00r"
    
    try:
        tester = DeviceActivationTester(email, password)
        
        # Connexion
        await tester.login()
        print("✅ Connexion réussie")
        
        # Récupérer l'appareil
        light_data = await tester.get_lightdata()
        if not light_data:
            print("❌ Aucun appareil trouvé")
            return
            
        print(f"📱 Appareil: {light_data['deviceName']}")
        print(f"🆔 ID: {light_data['id']}")
        print(f"💡 Luminosité initiale: {light_data['deviceLightRate']}")
        print()
        
        # Essayer d'activer l'appareil
        print("🔄 TENTATIVES D'ACTIVATION...")
        print("=" * 40)
        
        activation_results = await tester.test_device_activation()
        
        print("\n📋 RÉSUMÉ ACTIVATION:")
        print("-" * 30)
        working_activations = []
        for method, result in activation_results:
            if result and result.get("code") == "000":
                print(f"✅ {method}: SUCCÈS")
                working_activations.append(method)
            elif result:
                print(f"⚠️  {method}: Échec - {result.get('msg')}")
            else:
                print(f"❌ {method}: Aucune réponse")
        
        # Vérifier l'état après activation
        print(f"\n🔍 VÉRIFICATION ÉTAT POST-ACTIVATION...")
        is_started = await tester.check_device_status_after_activation()
        
        if is_started:
            print(f"🎉 APPAREIL DÉMARRÉ ! Tentative de contrôle...")
            
            # Maintenant essayer le contrôle
            print(f"\n🔆 Test contrôle avec appareil activé...")
            await tester.set_brightness(80)
            print("👀 REGARDEZ VOTRE LAMPE MAINTENANT !")
            await asyncio.sleep(5)
            
            await tester.set_brightness(20)
            print("👀 Retour luminosité normale...")
            
        else:
            print(f"😞 Appareil toujours pas démarré...")
            
        if working_activations:
            print(f"\n✅ Méthodes d'activation qui ont réussi: {', '.join(working_activations)}")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 