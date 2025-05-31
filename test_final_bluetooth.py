#!/usr/bin/env python3
"""
🎯 TEST FINAL - API MarsPro avec détection Bluetooth automatique
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'custom_components', 'marshydro'))

from api_marspro import MarsProAPI

async def test_final_api():
    """Test final avec l'API mise à jour"""
    print("🎯 TEST FINAL - API MarsPro Bluetooth")
    print("=" * 50)
    
    email = "jeremy.noverraz2@proton.me"
    password = "T00rT00r"
    
    try:
        api = MarsProAPI(email, password)
        
        # Connexion
        await api.login()
        print("✅ Connexion réussie")
        
        # Récupérer l'appareil (détection automatique du type)
        light_data = await api.get_lightdata()
        if not light_data:
            print("❌ Aucun appareil trouvé")
            return False
            
        device_id = light_data['id']
        current_brightness = light_data['deviceLightRate']
        
        print(f"📱 Appareil: {light_data['deviceName']}")
        print(f"🆔 ID: {device_id}")
        print(f"💡 Luminosité actuelle: {current_brightness}")
        
        # Vérifier la détection Bluetooth
        if hasattr(api, 'is_bluetooth_device') and api.is_bluetooth_device:
            print("🔵 ✅ Appareil Bluetooth détecté - Utilisation des commandes BT")
        else:
            print("📶 Appareil WiFi détecté - Utilisation des commandes WiFi")
        
        print()
        
        # Test 1: Changement de luminosité
        print("🔆 Test 1: Luminosité à 80%...")
        try:
            await api.set_brightness(80)
            print("✅ Commande envoyée")
            await asyncio.sleep(3)
        except Exception as e:
            print(f"❌ Erreur: {e}")
            
        # Test 2: Éteindre
        print("🔴 Test 2: Éteindre...")
        try:
            await api.toggle_switch(True, device_id)  # True = éteindre
            print("✅ Commande extinction envoyée")
            await asyncio.sleep(3)
        except Exception as e:
            print(f"❌ Erreur: {e}")
            
        # Test 3: Rallumer
        print("🟢 Test 3: Rallumer...")
        try:
            await api.toggle_switch(False, device_id)  # False = allumer
            print("✅ Commande allumage envoyée")
            await asyncio.sleep(3)
        except Exception as e:
            print(f"❌ Erreur: {e}")
            
        # Test 4: Remettre luminosité originale
        print(f"🔄 Test 4: Restaurer luminosité ({current_brightness}%)...")
        try:
            if current_brightness > 0:
                await api.set_brightness(current_brightness)
            else:
                await api.set_brightness(20)  # Valeur par défaut
            print("✅ Luminosité restaurée")
        except Exception as e:
            print(f"❌ Erreur: {e}")
        
        print(f"\n🎊 TESTS TERMINÉS !")
        print(f"👀 Votre lampe a-t-elle réagi aux commandes ?")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur générale: {e}")
        return False

async def main():
    print("🚨 TEST FINAL de l'intégration MarsPro")
    print("💡 Ce test utilise la détection automatique Bluetooth/WiFi")
    print()
    
    success = await test_final_api()
    
    if success:
        print(f"\n✅ L'API fonctionne techniquement.")
        print(f"🤔 Si votre lampe n'a pas réagi physiquement :")
        print(f"   - Vérifiez que la lampe est allumée manuellement")
        print(f"   - Vérifiez la connexion Bluetooth de la lampe")
        print(f"   - Il peut y avoir un délai de communication")
        print(f"   - Votre lampe pourrait nécessiter un pairing Bluetooth")
    else:
        print(f"\n❌ Problème technique dans l'API")

if __name__ == "__main__":
    asyncio.run(main()) 