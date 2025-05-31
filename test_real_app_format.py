#!/usr/bin/env python3
"""
🎯 TEST VRAI FORMAT APP - upDataStatus découvert !
"""

import asyncio
import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'custom_components', 'marshydro'))

from api_marspro import MarsProAPI

async def test_real_app_format():
    """Test avec le VRAI format upDataStatus de l'app"""
    print("🎯 TEST VRAI FORMAT APP MARSPRO")
    print("=" * 50)
    print("📱 Format exact capturé: upDataStatus")
    print()
    
    email = "jeremy.noverraz2@proton.me"
    password = "T00rT00r"
    
    try:
        api = MarsProAPI(email, password)
        
        # Connexion
        await api.login()
        print("✅ Connexion réussie")
        
        # Récupérer l'appareil
        light_data = await api.get_lightdata()
        if not light_data:
            print("❌ Aucun appareil trouvé")
            return False
            
        device_serial = light_data['deviceSerialnum']
        current_brightness = light_data['deviceLightRate']
        
        print(f"📱 Appareil: {light_data['deviceName']}")
        print(f"🔢 Serial (PID): {device_serial}")
        print(f"💡 Luminosité actuelle: {current_brightness}")
        print()
        
        # TEST 1: Format EXACT de vos captures - upDataStatus simple
        print("🧪 TEST 1: upDataStatus simple (comme capture)")
        print("-" * 50)
        
        # Format EXACT capturé !
        payload1 = {
            "data": json.dumps({
                "method": "upDataStatus",
                "params": {
                    "pid": device_serial
                }
            })
        }
        
        print(f"📝 Payload: {json.dumps(payload1, indent=2)}")
        result1 = await api._make_request("/api/upData/device", payload1)
        print(f"📤 Réponse: {json.dumps(result1, indent=2) if result1 else 'None'}")
        print("👀 REGARDEZ VOTRE LAMPE !")
        await asyncio.sleep(5)
        print()
        
        # TEST 2: upDataStatus avec paramètres de luminosité
        print("🧪 TEST 2: upDataStatus avec luminosité")
        print("-" * 50)
        
        payload2 = {
            "data": json.dumps({
                "method": "upDataStatus",
                "params": {
                    "pid": device_serial,
                    "rate": "80"  # Peut-être que rate = luminosité
                }
            })
        }
        
        print(f"📝 Payload: {json.dumps(payload2, indent=2)}")
        result2 = await api._make_request("/api/upData/device", payload2)
        print(f"📤 Réponse: {json.dumps(result2, indent=2) if result2 else 'None'}")
        print("👀 REGARDEZ VOTRE LAMPE !")
        await asyncio.sleep(5)
        print()
        
        # TEST 3: upDataStatus avec pwm
        print("🧪 TEST 3: upDataStatus avec PWM")
        print("-" * 50)
        
        payload3 = {
            "data": json.dumps({
                "method": "upDataStatus",
                "params": {
                    "pid": device_serial,
                    "pwm": "90"
                }
            })
        }
        
        print(f"📝 Payload: {json.dumps(payload3, indent=2)}")
        result3 = await api._make_request("/api/upData/device", payload3)
        print(f"📤 Réponse: {json.dumps(result3, indent=2) if result3 else 'None'}")
        print("👀 REGARDEZ VOTRE LAMPE !")
        await asyncio.sleep(5)
        print()
        
        # TEST 4: upDataStatus avec on/off
        print("🧪 TEST 4: upDataStatus OFF")
        print("-" * 50)
        
        payload4 = {
            "data": json.dumps({
                "method": "upDataStatus",
                "params": {
                    "pid": device_serial,
                    "on": "0"  # Éteindre
                }
            })
        }
        
        print(f"📝 Payload: {json.dumps(payload4, indent=2)}")
        result4 = await api._make_request("/api/upData/device", payload4)
        print(f"📤 Réponse: {json.dumps(result4, indent=2) if result4 else 'None'}")
        print("👀 LA LAMPE DOIT S'ÉTEINDRE !")
        await asyncio.sleep(5)
        print()
        
        # TEST 5: upDataStatus ON
        print("🧪 TEST 5: upDataStatus ON")
        print("-" * 50)
        
        payload5 = {
            "data": json.dumps({
                "method": "upDataStatus",
                "params": {
                    "pid": device_serial,
                    "on": "1"  # Rallumer
                }
            })
        }
        
        print(f"📝 Payload: {json.dumps(payload5, indent=2)}")
        result5 = await api._make_request("/api/upData/device", payload5)
        print(f"📤 Réponse: {json.dumps(result5, indent=2) if result5 else 'None'}")
        print("👀 LA LAMPE DOIT SE RALLUMER !")
        await asyncio.sleep(5)
        print()
        
        # Résumé
        print("📊 RÉSUMÉ TESTS upDataStatus")
        print("=" * 40)
        
        tests = [
            ("upDataStatus simple", result1),
            ("upDataStatus + rate", result2),
            ("upDataStatus + pwm", result3),
            ("upDataStatus OFF", result4),
            ("upDataStatus ON", result5)
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
        print(f"❓ VOTRE LAMPE A-T-ELLE ENFIN RÉAGI ?")
        
        if working_tests:
            print(f"✅ Méthodes qui marchent: {', '.join(working_tests)}")
            print(f"🎉 Si la lampe a bougé = PROBLÈME RÉSOLU !")
        
        return len(working_tests) > 0
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

async def main():
    print("🚨 TEST DÉCISIF avec le VRAI format de l'app !")
    print("📱 Méthode: upDataStatus (pas outletCtrl)")
    print()
    
    success = await test_real_app_format()
    
    if success:
        print(f"\n🎉 **ENFIN ! LE VRAI FORMAT TROUVÉ !** 🎉")
        print(f"🔧 La méthode correcte est: upDataStatus")
        print(f"📱 Nous pouvons maintenant mettre à jour l'API !")
    else:
        print(f"\n😔 Même avec upDataStatus, ça ne marche pas...")

if __name__ == "__main__":
    asyncio.run(main()) 