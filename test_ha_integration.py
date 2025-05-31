#!/usr/bin/env python3
"""
🏠 TEST INTÉGRATION HOME ASSISTANT MISE À JOUR
Test de l'intégration avec support Bluetooth BLE et WiFi hybride
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'custom_components', 'marshydro'))

from api_marspro import MarsProAPI

async def test_ha_integration():
    """Test de l'intégration HA mise à jour"""
    print("🏠 TEST INTÉGRATION HOME ASSISTANT")
    print("=" * 50)
    print("🔧 Version 2.3.0 avec support Bluetooth BLE + WiFi")
    print()
    
    email = "jeremy.noverraz2@proton.me"
    password = "T00rT00r"
    
    try:
        # Initialiser l'API
        api = MarsProAPI(email, password)
        await api.login()
        print("✅ Connexion API réussie")
        
        # Détecter le mode de l'appareil
        print("\n🔍 DÉTECTION MODE APPAREIL")
        print("-" * 30)
        
        mode_detected = await api.detect_device_mode()
        
        if mode_detected:
            if api.is_bluetooth_device:
                print("🔵 ✅ Mode Bluetooth détecté")
                if api.bluetooth_support:
                    print("📱 ✅ Support Bluetooth BLE disponible")
                    if api.ble_device:
                        print(f"🎯 ✅ Appareil BLE trouvé: {api.ble_device.name}")
                    else:
                        print("⚠️  Appareil BLE non trouvé (vérifiez qu'il est allumé)")
                else:
                    print("❌ Support Bluetooth BLE non disponible (bleak manquant)")
            else:
                print("📶 ✅ Mode WiFi/Cloud détecté")
        else:
            print("❌ Détection de mode échouée")
        
        print()
        
        # Test de contrôle hybride
        print("🎛️ TEST CONTRÔLE HYBRIDE")
        print("-" * 30)
        
        test_sequences = [
            {"on": True, "pwm": 100, "desc": "Allumer à 100%"},
            {"on": True, "pwm": 50, "desc": "Réduire à 50%"},
            {"on": True, "pwm": 25, "desc": "Réduire à 25%"},
            {"on": True, "pwm": 80, "desc": "Augmenter à 80%"},
            {"on": False, "pwm": 0, "desc": "Éteindre"}
        ]
        
        for i, test in enumerate(test_sequences, 1):
            print(f"\n🧪 Test {i}: {test['desc']}")
            
            try:
                success = await api.control_device_hybrid(test['on'], test['pwm'])
                
                if success:
                    print(f"   ✅ {test['desc']} - Commande envoyée")
                    if api.is_bluetooth_device:
                        print("   🔵 Via Bluetooth BLE direct")
                    else:
                        print("   📶 Via API Cloud")
                else:
                    print(f"   ❌ {test['desc']} - Échec")
                    
            except Exception as e:
                print(f"   ❌ {test['desc']} - Erreur: {e}")
            
            # Attente entre commandes
            await asyncio.sleep(3)
        
        print("\n" + "=" * 50)
        print("🏁 TEST TERMINÉ")
        print()
        print("📋 RÉSULTATS POUR HOME ASSISTANT:")
        
        if api.is_bluetooth_device:
            print("🔵 APPAREIL BLUETOOTH:")
            print("   • L'intégration utilise Bluetooth BLE direct")
            print("   • Pas besoin de configuration WiFi")
            print("   • Communication locale instantanée")
            print("   • Fonctionne même sans internet")
        else:
            print("📶 APPAREIL WIFI:")
            print("   • L'intégration utilise l'API cloud")
            print("   • Nécessite connexion internet")
            print("   • Appareil doit être connecté au WiFi")
        
        print()
        print("🔧 INSTALLATION DANS HOME ASSISTANT:")
        print("   1. Copier le dossier custom_components/marshydro")
        print("   2. Redémarrer Home Assistant")
        print("   3. Aller dans Intégrations → Ajouter → Mars Hydro")
        print("   4. Entrer email/mot de passe MarsPro")
        print("   5. L'intégration détectera automatiquement le mode")
        
    except Exception as e:
        print(f"❌ Erreur test: {e}")
        import traceback
        traceback.print_exc()

async def test_light_entity_simulation():
    """Simuler le comportement de l'entité light de HA"""
    print("\n💡 SIMULATION ENTITÉ LIGHT HOME ASSISTANT")
    print("=" * 50)
    
    email = "jeremy.noverraz2@proton.me"
    password = "T00rT00r"
    
    try:
        # Simuler l'initialisation comme dans HA
        api = MarsProAPI(email, password)
        await api.login()
        
        # Récupérer les données de l'appareil
        device_data = await api.get_lightdata()
        
        if device_data:
            device_name = device_data.get('deviceName', 'Unknown')
            device_id = device_data.get('id')
            brightness_rate = device_data.get('deviceLightRate', 0)
            
            print(f"📱 Appareil: {device_name}")
            print(f"🆔 ID: {device_id}")
            print(f"💡 Luminosité actuelle: {brightness_rate}%")
            print()
            
            # Simuler les appels de HA
            print("🏠 Simulation appels Home Assistant:")
            print("-" * 40)
            
            # Simulation: Allumer à 75%
            print("1. Appel: light.turn_on(brightness=192)  # 75%")
            brightness_ha = 192  # HA utilise 0-255
            brightness_percent = round((brightness_ha / 255) * 100)
            is_on = brightness_ha > 0
            
            success = await api.control_device_hybrid(is_on, brightness_percent)
            print(f"   Résultat: {'✅ Succès' if success else '❌ Échec'}")
            
            await asyncio.sleep(2)
            
            # Simulation: Éteindre
            print("2. Appel: light.turn_off()")
            success = await api.control_device_hybrid(False, 0)
            print(f"   Résultat: {'✅ Succès' if success else '❌ Échec'}")
            
            print()
            print("💡 L'intégration HA devrait maintenant fonctionner !")
            
        else:
            print("❌ Impossible de récupérer les données de l'appareil")
            
    except Exception as e:
        print(f"❌ Erreur simulation: {e}")

if __name__ == "__main__":
    asyncio.run(test_ha_integration())
    asyncio.run(test_light_entity_simulation()) 