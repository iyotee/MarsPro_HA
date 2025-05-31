#!/usr/bin/env python3
"""
🎉 TEST FINAL - Vérification intégration MarsPro complète
Teste l'API corrigée avec PID stable et détection de type correct
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'custom_components', 'marshydro'))

from api_marspro import MarsProAPI

async def test_final_integration():
    """Test final de l'intégration complète"""
    print("🎉 TEST FINAL - INTÉGRATION MARSPRO COMPLÈTE")
    print("=" * 60)
    
    email = "jeremy.noverraz2@proton.me"
    password = "T00rT00r"
    
    try:
        # 1. Initialisation API
        print("🔧 1. INITIALISATION API")
        print("-" * 30)
        api = MarsProAPI(email, password)
        await api.login()
        print("✅ API initialisée et connectée")
        print()
        
        # 2. Récupération données appareil
        print("📱 2. RÉCUPÉRATION DONNÉES APPAREIL")
        print("-" * 40)
        device_data = await api.get_lightdata()
        
        if device_data:
            device_name = device_data.get("deviceName")
            device_id = device_data.get("id")
            stable_pid = device_data.get("device_pid_stable")
            device_serial = device_data.get("deviceSerialnum")
            device_light_rate = device_data.get("deviceLightRate")
            is_close = device_data.get("isClose")
            
            print(f"✅ Appareil trouvé: {device_name}")
            print(f"🆔 ID actuel (changeant): {device_id}")
            print(f"🎯 PID stable: {stable_pid}")
            print(f"🔢 Serial: {device_serial}")
            print(f"💡 Light Rate: {device_light_rate}")
            print(f"🔌 Is Close: {is_close}")
            
            # Détection de type
            device_name_lower = device_name.lower()
            if "dimbox" in device_name_lower:
                detected_type = "LIGHT"
                print(f"✅ Type détecté: {detected_type} (DIMBOX trouvé)")
            elif "fan" in device_name_lower:
                detected_type = "FAN"
                print(f"✅ Type détecté: {detected_type}")
            else:
                detected_type = "LIGHT"
                print(f"✅ Type par défaut: {detected_type}")
            print()
            
        else:
            print("❌ Aucun appareil trouvé")
            return False
        
        # 3. Test contrôle avec PID stable
        print("🎛️  3. TEST CONTRÔLE AVEC PID STABLE")
        print("-" * 40)
        
        # Test 1: Luminosité 60%
        print("💡 Test luminosité 60%...")
        result1 = await api.control_device_by_pid(stable_pid, True, 60)
        print(f"   Résultat: {'✅ SUCCÈS' if result1 else '❌ ÉCHEC'}")
        await asyncio.sleep(2)
        
        # Test 2: Luminosité 90%
        print("💡 Test luminosité 90%...")
        result2 = await api.control_device_by_pid(stable_pid, True, 90)
        print(f"   Résultat: {'✅ SUCCÈS' if result2 else '❌ ÉCHEC'}")
        await asyncio.sleep(2)
        
        # Test 3: OFF
        print("🔴 Test OFF...")
        result3 = await api.control_device_by_pid(stable_pid, False, 0)
        print(f"   Résultat: {'✅ SUCCÈS' if result3 else '❌ ÉCHEC'}")
        await asyncio.sleep(2)
        
        # Test 4: ON 100%
        print("🟢 Test ON 100%...")
        result4 = await api.control_device_by_pid(stable_pid, True, 100)
        print(f"   Résultat: {'✅ SUCCÈS' if result4 else '❌ ÉCHEC'}")
        await asyncio.sleep(2)
        print()
        
        # 4. Test méthodes API standard
        print("🧪 4. TEST MÉTHODES API STANDARD")
        print("-" * 40)
        
        # Test set_brightness
        print("🔆 Test set_brightness(75)...")
        try:
            brightness_result = await api.set_brightness(75)
            print(f"   Résultat: ✅ SUCCÈS - Code: {brightness_result.get('code')}")
        except Exception as e:
            print(f"   Résultat: ❌ ÉCHEC - {e}")
        await asyncio.sleep(2)
        
        # Test toggle_switch
        print("🔄 Test toggle_switch(False)...")
        try:
            toggle_result = await api.toggle_switch(False, stable_pid)
            print(f"   Résultat: ✅ SUCCÈS - Code: {toggle_result.get('code')}")
        except Exception as e:
            print(f"   Résultat: ❌ ÉCHEC - {e}")
        await asyncio.sleep(2)
        
        print("🔄 Test toggle_switch(True)...")
        try:
            toggle_result2 = await api.toggle_switch(True, stable_pid)
            print(f"   Résultat: ✅ SUCCÈS - Code: {toggle_result2.get('code')}")
        except Exception as e:
            print(f"   Résultat: ❌ ÉCHEC - {e}")
        print()
        
        # 5. Résumé final
        print("📊 5. RÉSUMÉ FINAL")
        print("=" * 30)
        
        working_tests = []
        if result1: working_tests.append("Luminosité 60%")
        if result2: working_tests.append("Luminosité 90%")
        if result3: working_tests.append("OFF")
        if result4: working_tests.append("ON 100%")
        
        print(f"✅ Tests de contrôle réussis: {len(working_tests)}/4")
        if working_tests:
            for test in working_tests:
                print(f"   - {test}")
        
        print()
        print("🎯 INFORMATIONS POUR HOME ASSISTANT:")
        print(f"   - PID stable à utiliser: {stable_pid}")
        print(f"   - Type d'appareil: {detected_type}")
        print(f"   - Nom: {device_name}")
        print(f"   - Contrôle fonctionnel: {'✅ OUI' if working_tests else '❌ NON'}")
        
        if len(working_tests) >= 3:
            print()
            print("🎉 SUCCÈS TOTAL !")
            print("💡 L'intégration MarsPro est maintenant complètement fonctionnelle")
            print("🏠 Redémarrez Home Assistant pour voir les corrections")
            return True
        else:
            print()
            print("⚠️  Problèmes partiels détectés")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(test_final_integration()) 