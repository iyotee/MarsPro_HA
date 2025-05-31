#!/usr/bin/env python3
"""
🔵 TEST COMMANDE setDeviceActiveV
Basé sur la découverte des captures réseau HTTP Toolkit
"""

import asyncio
import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'custom_components', 'marshydro'))

from api_marspro import MarsProAPI

async def test_device_activation():
    """Test de la commande setDeviceActiveV découverte dans les captures"""
    print("🔵 TEST COMMANDE setDeviceActiveV")
    print("=" * 50)
    print("🎯 Basé sur les captures réseau HTTP Toolkit")
    print()
    
    email = "jeremy.noverraz2@proton.me"
    password = "T00rT00r"
    
    try:
        api = MarsProAPI(email, password)
        await api.login()
        print("✅ Connexion réussie")
        
        # Récupérer les infos de l'appareil
        device_data = await api.get_lightdata()
        if not device_data:
            print("❌ Aucun appareil trouvé")
            return
        
        device_name = device_data.get('deviceName', 'Mars Pro')
        user_id = api.user_id  # 17866
        
        print(f"📱 Appareil: {device_name}")
        print(f"👤 User ID: {user_id}")
        print()
        
        # TEST 1: setDeviceActiveV (comme dans les captures)
        print("🧪 TEST 1: setDeviceActiveV (activation appareil)")
        print("-" * 40)
        
        inner_data = {
            "method": "setDeviceActiveV",
            "params": {
                "vid": str(user_id),  # 17866
                "unum": device_name,  # "Mars Pro" 
                "tOffset": 120        # Offset de temps (peut-être timezone?)
            }
        }
        
        payload = {
            "data": json.dumps(inner_data)
        }
        
        print(f"📝 Payload setDeviceActiveV:")
        print(f"   {json.dumps(payload, indent=2)}")
        
        response = await api._make_request("/api/upData/device", payload)
        print(f"📤 Réponse: {json.dumps(response, indent=2) if response else 'None'}")
        
        if response and response.get('code') == '000':
            print("✅ ACTIVATION RÉUSSIE !")
            print("💡 L'appareil devrait maintenant être 'réveillé'")
        else:
            print("❌ Activation échouée")
        
        print()
        
        # TEST 2: Maintenant essayer le contrôle normal APRÈS activation
        print("🧪 TEST 2: Contrôle PWM APRÈS activation")
        print("-" * 40)
        
        await asyncio.sleep(2)  # Attendre que l'activation prenne effet
        
        # Utiliser le PID extrait
        pid = device_data.get('device_pid_stable', '345F45EC73CC')
        
        inner_data_control = {
            "method": "outletCtrl",
            "params": {
                "pid": pid,
                "num": 0,
                "on": 1,
                "pwm": 75
            }
        }
        
        payload_control = {
            "data": json.dumps(inner_data_control)
        }
        
        print(f"📝 Payload contrôle:")
        print(f"   {json.dumps(payload_control, indent=2)}")
        
        response2 = await api._make_request("/api/upData/device", payload_control)
        print(f"📤 Réponse: {json.dumps(response2, indent=2) if response2 else 'None'}")
        
        if response2 and response2.get('code') == '000':
            print("✅ COMMANDE CONTRÔLE ENVOYÉE !")
            print("💡 La lampe devrait maintenant être à 75%")
        else:
            print("❌ Commande contrôle échouée")
        
        print()
        
        # TEST 3: Essayer plusieurs valeurs maintenant que l'appareil est actif
        test_values = [50, 100, 20, 0]  # 0 = éteindre
        
        for pwm in test_values:
            print(f"🧪 TEST: PWM {pwm}%")
            
            inner_data_test = {
                "method": "outletCtrl", 
                "params": {
                    "pid": pid,
                    "num": 0,
                    "on": 1 if pwm > 0 else 0,
                    "pwm": pwm
                }
            }
            
            payload_test = {"data": json.dumps(inner_data_test)}
            response_test = await api._make_request("/api/upData/device", payload_test)
            
            if response_test and response_test.get('code') == '000':
                print(f"   ✅ PWM {pwm}% envoyé")
            else:
                print(f"   ❌ PWM {pwm}% échec")
            
            await asyncio.sleep(2)  # Attendre entre chaque commande
        
        print("\n" + "=" * 50)
        print("🏁 TESTS TERMINÉS")
        print()
        print("🔍 QUESTIONS CRITIQUES:")
        print("   1. La lampe a-t-elle réagi APRÈS le setDeviceActiveV ?")
        print("   2. Y a-t-il eu une différence avant/après activation ?")
        print("   3. Les changements de luminosité sont-ils visibles maintenant ?")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

async def test_other_activation_methods():
    """Tester d'autres méthodes d'activation possibles"""
    print("\n🔧 TEST AUTRES MÉTHODES D'ACTIVATION")
    print("=" * 50)
    
    email = "jeremy.noverraz2@proton.me"
    password = "T00rT00r"
    
    try:
        api = MarsProAPI(email, password)
        await api.login()
        
        device_data = await api.get_lightdata()
        device_name = device_data.get('deviceName', 'Mars Pro')
        user_id = api.user_id
        
        # Autres méthodes d'activation possibles
        activation_methods = [
            {
                "method": "deviceWakeUp",
                "params": {"deviceName": device_name}
            },
            {
                "method": "bluetoothActivate", 
                "params": {"vid": str(user_id), "deviceName": device_name}
            },
            {
                "method": "setDeviceOnline",
                "params": {"deviceName": device_name, "status": "online"}
            }
        ]
        
        for i, method_data in enumerate(activation_methods, 1):
            print(f"\n🧪 TEST {i}: {method_data['method']}")
            
            payload = {"data": json.dumps(method_data)}
            response = await api._make_request("/api/upData/device", payload)
            
            print(f"📤 Réponse: {json.dumps(response, indent=2) if response else 'None'}")
            
            if response and response.get('code') == '000':
                print(f"✅ {method_data['method']} réussi")
            else:
                print(f"❌ {method_data['method']} échec")
            
            await asyncio.sleep(1)
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    asyncio.run(test_device_activation())
    asyncio.run(test_other_activation_methods()) 