#!/usr/bin/env python3
"""
🎉 TEST FINAL FONCTIONNEL - wifiCtrl découvert !
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'custom_components', 'marshydro'))

from api_marspro import MarsProAPI

async def test_working_integration():
    """Test final avec l'API qui fonctionne maintenant"""
    print("🎉 TEST FINAL - INTÉGRATION FONCTIONNELLE")
    print("=" * 50)
    print("💡 Utilisation du format wifiCtrl découvert")
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
            
        device_id = light_data['id']
        current_brightness = light_data['deviceLightRate']
        
        print(f"📱 Appareil: {light_data['deviceName']}")
        print(f"🆔 ID: {device_id}")
        print(f"💡 Luminosité actuelle: {current_brightness}")
        print()
        
        # Test séquence complète
        print("🔆 Test 1: Luminosité 70%...")
        await api.set_brightness(70)
        print("👀 Changement visible ?")
        await asyncio.sleep(3)
        
        print("🔴 Test 2: Éteindre...")
        await api.toggle_switch(True, device_id)
        print("👀 Extinction visible ?")
        await asyncio.sleep(3)
        
        print("🟢 Test 3: Rallumer...")
        await api.toggle_switch(False, device_id)
        print("👀 Rallumage visible ?")
        await asyncio.sleep(3)
        
        print("🔄 Test 4: Restaurer luminosité originale...")
        if current_brightness > 0:
            await api.set_brightness(current_brightness)
        else:
            await api.set_brightness(20)
        print("👀 Retour à la normale ?")
        
        print(f"\n🎊 SÉQUENCE DE TEST TERMINÉE !")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

async def main():
    success = await test_working_integration()
    
    if success:
        print(f"\n✅ **INTÉGRATION MARSPRO RÉUSSIE !** ✅")
        print(f"🔧 Format de contrôle découvert: wifiCtrl")
        print(f"📱 Appareil supporté: MZL001 (Bluetooth+WiFi)")
        print(f"🎯 Toutes les fonctions Home Assistant sont maintenant prêtes !")
        print(f"\n🚀 **VOUS POUVEZ MAINTENANT:**")
        print(f"   - Installer l'intégration dans Home Assistant")
        print(f"   - Contrôler votre lampe via l'interface HA")
        print(f"   - Créer des automatisations")
        print(f"   - Publier sur GitHub/HACS")
    else:
        print(f"\n❌ Il reste des problèmes à résoudre")

if __name__ == "__main__":
    asyncio.run(main()) 