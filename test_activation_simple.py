#!/usr/bin/env python3
"""
🔵 TEST SIMPLE - setDeviceActiveV
Test de la commande d'activation découverte dans les captures
"""

import asyncio
import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'custom_components', 'marshydro'))

from api_marspro import MarsProAPI

async def test_activation():
    print("🔵 TEST setDeviceActiveV")
    print("=" * 40)
    
    email = "jeremy.noverraz2@proton.me"
    password = "T00rT00r"
    
    try:
        api = MarsProAPI(email, password)
        await api.login()
        print("✅ Connecté")
        
        # Récupérer appareil
        device_data = await api.get_lightdata()
        if not device_data:
            print("❌ Pas d'appareil")
            return
        
        device_name = device_data.get('deviceName', 'Mars Pro')
        user_id = str(api.user_id)
        
        print(f"📱 Appareil: {device_name}")
        print(f"👤 UserID: {user_id}")
        print()
        
        # TEST: setDeviceActiveV (exactement comme dans vos captures)
        print("🧪 Envoi setDeviceActiveV...")
        
        inner_data = {
            "method": "setDeviceActiveV",
            "params": {
                "vid": user_id,      # "17866"
                "unum": device_name, # "Mars Pro"
                "tOffset": 120       # Timezone offset
            }
        }
        
        payload = {
            "data": json.dumps(inner_data)
        }
        
        print(f"📝 Envoi: {json.dumps(inner_data, indent=2)}")
        
        response = await api._make_request("/api/upData/device", payload)
        print(f"📤 Réponse: {response}")
        
        if response and response.get('code') == '000':
            print("✅ ACTIVATION RÉUSSIE !")
            print("💡 Maintenant test contrôle...")
            
            # Attendre un peu
            await asyncio.sleep(3)
            
            # Essayer le contrôle maintenant
            pid = device_data.get('device_pid_stable', '345F45EC73CC')
            
            control_data = {
                "method": "outletCtrl",
                "params": {
                    "pid": pid,
                    "num": 0,
                    "on": 1,
                    "pwm": 80
                }
            }
            
            control_payload = {"data": json.dumps(control_data)}
            
            print(f"🔆 Test contrôle 80%...")
            response2 = await api._make_request("/api/upData/device", control_payload)
            print(f"📤 Réponse contrôle: {response2}")
            
            if response2 and response2.get('code') == '000':
                print("✅ CONTRÔLE ENVOYÉ !")
                print("👀 REGARDEZ VOTRE LAMPE !")
            else:
                print("❌ Contrôle échec")
        else:
            print("❌ Activation échec")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    asyncio.run(test_activation()) 