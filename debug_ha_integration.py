#!/usr/bin/env python3
"""
🔍 DEBUG INTÉGRATION HOME ASSISTANT
Teste exactement ce que fait HA avec l'API MarsPro
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'custom_components', 'marshydro'))

from api_marspro import MarsProAPI

async def debug_ha_flow():
    """Simuler exactement le flow de Home Assistant"""
    print("🔍 DEBUG INTÉGRATION HOME ASSISTANT")
    print("=" * 50)
    print("💡 Simulation exacte du flow HA")
    print()
    
    email = "jeremy.noverraz2@proton.me"
    password = "T00rT00r"
    
    try:
        # 1. Création API (comme dans __init__.py)
        print("🔧 1. CRÉATION API (comme __init__.py)")
        print("-" * 40)
        api = MarsProAPI(email, password)
        await api.login()
        print("✅ API créée et connectée")
        
        # 2. get_lightdata() (comme dans __init__.py)
        print("\n📱 2. GET_LIGHTDATA (comme __init__.py)")
        print("-" * 40)
        device_data = await api.get_lightdata()
        
        if device_data:
            device_name = device_data.get("deviceName")
            device_id = device_data.get("id")
            stable_pid = device_data.get("device_pid_stable")
            device_serial = device_data.get("deviceSerialnum")
            
            print(f"✅ Données récupérées:")
            print(f"   Nom: {device_name}")
            print(f"   ID: {device_id}")
            print(f"   PID stable: {stable_pid}")
            print(f"   Serial: {device_serial}")
            
            # Test détection de type (comme dans __init__.py)
            device_name_lower = device_name.lower()
            if "dimbox" in device_name_lower or "light" in device_name_lower:
                device_type = "Light"
                print(f"✅ Type détecté: {device_type}")
            elif "fan" in device_name_lower or "wind" in device_name_lower:
                device_type = "Fan" 
                print(f"✅ Type détecté: {device_type}")
            else:
                device_type = "Light"  # Default
                print(f"✅ Type par défaut: {device_type}")
        else:
            print("❌ get_lightdata() a retourné None")
            return False
        
        # 3. Test light.py async_update()
        print("\n💡 3. TEST LIGHT.PY ASYNC_UPDATE")
        print("-" * 40)
        
        # Simuler ce que fait light.py
        light_data = await api.get_lightdata()
        if light_data:
            device_id = light_data.get("id")
            stable_pid = (light_data.get("device_pid_stable") or 
                         light_data.get("deviceSerialnum") or 
                         str(light_data.get("id", "")))
            device_name = light_data.get("deviceName")
            
            # Gérer deviceLightRate
            light_rate = light_data.get("deviceLightRate")
            is_close = light_data.get("isClose", False)
            
            print(f"📊 État de l'appareil:")
            print(f"   Device ID: {device_id}")
            print(f"   Stable PID: {stable_pid}")
            print(f"   Device Name: {device_name}")
            print(f"   Light Rate: {light_rate}")
            print(f"   Is Close: {is_close}")
            
            if light_rate == -1:
                if is_close:
                    brightness = 0
                    state = False
                    print(f"   → Brightness: 0 (OFF)")
                    print(f"   → State: False")
                else:
                    brightness = 255
                    state = True
                    print(f"   → Brightness: 255 (ON, full)")
                    print(f"   → State: True")
            else:
                brightness = int((light_rate / 100) * 255) if light_rate else 0
                state = not is_close
                print(f"   → Brightness: {brightness}")
                print(f"   → State: {state}")
            
            print("✅ Simulation light.py réussie")
        else:
            print("❌ light.py ne peut pas récupérer les données")
            return False
        
        # 4. Test contrôle
        print("\n🎛️  4. TEST CONTRÔLE (comme dans light.py)")
        print("-" * 40)
        
        try:
            # Test set_brightness comme dans light.py
            print("🔆 Test set_brightness(50)...")
            result = await api.set_brightness(50)
            if result and result.get("code") == "000":
                print("✅ set_brightness réussi")
            else:
                print(f"❌ set_brightness échoué: {result}")
        except Exception as e:
            print(f"❌ Exception set_brightness: {e}")
        
        # 5. Résumé pour HA
        print("\n📊 5. RÉSUMÉ POUR HOME ASSISTANT")
        print("=" * 40)
        
        print(f"🏠 Configuration HA:")
        print(f"   Identifiant stable: {stable_pid}")
        print(f"   Nom appareil: {device_name}")
        print(f"   Type: {device_type}")
        print(f"   Modèle: MarsPro {device_type}")
        
        if stable_pid and device_name:
            print(f"\n✅ L'intégration DEVRAIT fonctionner !")
            print(f"💡 Si ça ne marche pas, problème dans HA lui-même")
        else:
            print(f"\n❌ Données manquantes pour HA")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur dans le flow: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(debug_ha_flow()) 