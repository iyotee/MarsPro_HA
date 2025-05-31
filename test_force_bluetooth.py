#!/usr/bin/env python3
"""
🔵 TEST FORCÉ BLUETOOTH - Commandes BT explicites pour MZL001
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'custom_components', 'marshydro'))

from api_marspro import MarsProAPI

async def test_force_bluetooth():
    """Test avec commandes Bluetooth forcées"""
    print("🔵 TEST FORCÉ BLUETOOTH MZL001")
    print("=" * 50)
    
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
            
        device_id = light_data['id']
        device_serial = light_data['deviceSerialnum']
        current_brightness = light_data['deviceLightRate']
        
        print(f"📱 Appareil: {light_data['deviceName']}")
        print(f"🆔 ID: {device_id}")
        print(f"🔢 Serial: {device_serial}")
        print(f"💡 Luminosité: {current_brightness}")
        print()
        
        # FORCER le mode Bluetooth
        api.is_bluetooth_device = True
        api.device_serial = device_serial
        print("🔵 ✅ MODE BLUETOOTH FORCÉ")
        print()
        
        # Test 1: Wakeup explicite
        print("⏰ Test 1: Wakeup Bluetooth...")
        await api._wakeup_bluetooth_device()
        await asyncio.sleep(2)
        
        # Test 2: Luminosité 90% (Bluetooth)
        print("🔆 Test 2: Luminosité 90% (Bluetooth)...")
        try:
            await api.set_brightness(90)
            print("✅ Commande Bluetooth envoyée")
            print("👀 REGARDEZ VOTRE LAMPE MAINTENANT !")
            await asyncio.sleep(4)
        except Exception as e:
            print(f"❌ Erreur: {e}")
            
        # Test 3: Switch OFF (Bluetooth)
        print("🔴 Test 3: Éteindre (Bluetooth)...")
        try:
            await api.toggle_switch(True, device_id)
            print("✅ Commande extinction Bluetooth envoyée")
            print("👀 LA LAMPE DOIT S'ÉTEINDRE !")
            await asyncio.sleep(4)
        except Exception as e:
            print(f"❌ Erreur: {e}")
            
        # Test 4: Switch ON (Bluetooth)
        print("🟢 Test 4: Rallumer (Bluetooth)...")
        try:
            await api.toggle_switch(False, device_id)
            print("✅ Commande rallumage Bluetooth envoyée")
            print("👀 LA LAMPE DOIT SE RALLUMER !")
            await asyncio.sleep(4)
        except Exception as e:
            print(f"❌ Erreur: {e}")
            
        # Test 5: Remettre luminosité originale
        print(f"🔄 Test 5: Restaurer {current_brightness}% (Bluetooth)...")
        try:
            if current_brightness > 0:
                await api.set_brightness(current_brightness)
            else:
                await api.set_brightness(20)
            print("✅ Luminosité restaurée")
            await asyncio.sleep(2)
        except Exception as e:
            print(f"❌ Erreur: {e}")
        
        print(f"\n🎊 TESTS BLUETOOTH TERMINÉS !")
        print(f"❓ VOTRE LAMPE A-T-ELLE RÉAGI ?")
        print(f"   - Changement de luminosité visible ?")
        print(f"   - Extinction/rallumage visible ?")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur générale: {e}")
        return False

async def main():
    print("🚨 ATTENTION: Test avec commandes Bluetooth FORCÉES")
    print("🔵 Spécialement conçu pour votre MZL001")
    print()
    
    success = await test_force_bluetooth()
    
    if success:
        print(f"\n🔵 LES COMMANDES BLUETOOTH ONT ÉTÉ ENVOYÉES")
        print(f"✅ Si votre lampe a réagi = SUCCÈS TOTAL !")
        print(f"❌ Si rien ne s'est passé = Problème de communication Bluetooth")
        print(f"\n💡 Votre lampe est peut-être :")
        print(f"   - En mode veille profonde")
        print(f"   - Trop éloignée du hub Bluetooth")
        print(f"   - Non appairée avec le système")
    else:
        print(f"\n❌ Échec technique des commandes")

if __name__ == "__main__":
    asyncio.run(main()) 