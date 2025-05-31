#!/usr/bin/env python3
"""
🔵 TEST EXACT - Reproduction captures HTTP Toolkit
Reproduit EXACTEMENT les commandes de vos captures
"""

import asyncio
import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'custom_components', 'marshydro'))

from api_marspro import MarsProAPI

async def test_exact_capture():
    print("🔵 REPRODUCTION EXACTE DES CAPTURES")
    print("=" * 50)
    
    email = "jeremy.noverraz2@proton.me"
    password = "T00rT00r"
    
    try:
        api = MarsProAPI(email, password)
        await api.login()
        print("✅ Connecté")
        
        device_data = await api.get_lightdata()
        device_name = device_data.get('deviceName', 'Mars Pro')
        user_id = str(api.user_id)  # "17866"
        
        print(f"📱 Appareil: {device_name}")
        print(f"👤 UserID: {user_id}")
        print()
        
        # EXACTEMENT comme dans vos captures :
        # {"data": "{\"method\":\"setDeviceActiveV\",\"params\":{\"vid\":\"17866\",\"unum\":\"Mars Pro\",\"tOffset\":120}}"}
        
        print("🧪 TEST EXACT de vos captures...")
        
        inner_data = {
            "method": "setDeviceActiveV",
            "params": {
                "vid": user_id,        # "17866"
                "unum": "Mars Pro",    # EXACTEMENT "Mars Pro" comme dans les captures
                "tOffset": 120         # 120 comme dans les captures
            }
        }
        
        payload = {
            "data": json.dumps(inner_data)
        }
        
        print(f"📝 Payload EXACT (comme captures):")
        print(f"   {json.dumps(payload)}")
        print()
        
        response = await api._make_request("/api/upData/device", payload)
        print(f"📤 Réponse setDeviceActiveV: {response}")
        
        if response and response.get('code') == '000':
            print("✅ ACTIVATION EXACTE RÉUSSIE !")
            
            # Attendre un peu (comme l'app fait probablement)
            print("⏳ Attente 5 secondes (stabilisation)...")
            await asyncio.sleep(5)
            
            # Maintenant essayer le contrôle de luminosité
            pid = device_data.get('device_pid_stable', '345F45EC73CC')
            
            # Tests multiples comme l'app fait probablement
            test_sequences = [
                {"pwm": 100, "desc": "Maximum 100%"},
                {"pwm": 50, "desc": "Moyen 50%"},
                {"pwm": 25, "desc": "Faible 25%"},
                {"pwm": 75, "desc": "Fort 75%"}
            ]
            
            for test in test_sequences:
                print(f"\n🔆 Test {test['desc']}...")
                
                control_data = {
                    "method": "outletCtrl",
                    "params": {
                        "pid": pid,
                        "num": 0,
                        "on": 1,
                        "pwm": test['pwm']
                    }
                }
                
                control_payload = {"data": json.dumps(control_data)}
                
                response2 = await api._make_request("/api/upData/device", control_payload)
                
                if response2 and response2.get('code') == '000':
                    print(f"   ✅ {test['desc']} envoyé")
                    print(f"   👀 Lampe devrait être à {test['pwm']}%")
                else:
                    print(f"   ❌ {test['desc']} échec: {response2}")
                
                # Attente entre chaque commande
                await asyncio.sleep(3)
            
            # Test final: éteindre
            print(f"\n🌙 Test extinction...")
            
            off_data = {
                "method": "outletCtrl",
                "params": {
                    "pid": pid,
                    "num": 0,
                    "on": 0,
                    "pwm": 0
                }
            }
            
            off_payload = {"data": json.dumps(off_data)}
            response3 = await api._make_request("/api/upData/device", off_payload)
            
            if response3 and response3.get('code') == '000':
                print(f"   ✅ Extinction envoyée")
                print(f"   👀 Lampe devrait s'éteindre")
            else:
                print(f"   ❌ Extinction échec: {response3}")
                
        else:
            print("❌ Activation exacte échec")
            print(f"   Réponse: {response}")
        
        print("\n" + "=" * 50)
        print("🏁 REPRODUCTION TERMINÉE")
        print()
        print("🔍 QUESTION CRITIQUE:")
        print("   Avec le setDeviceActiveV EXACT (unum='Mars Pro'),")
        print("   votre lampe a-t-elle enfin réagi ?")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_exact_capture()) 