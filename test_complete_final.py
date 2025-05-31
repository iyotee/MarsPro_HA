#!/usr/bin/env python3
"""
🎯 TEST ULTRA-COMPLET MARSPRO
Test de TOUTES les méthodes de contrôle possibles
"""

import asyncio
import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'custom_components', 'marshydro'))

from api_marspro import MarsProAPI

async def ultra_complete_test():
    """Test ultra-complet de toutes les méthodes"""
    print("🎯 TEST ULTRA-COMPLET MARSPRO")
    print("=" * 60)
    print("🔧 Test de TOUTES les méthodes de contrôle possibles")
    print()
    
    email = "jeremy.noverraz2@proton.me"
    password = "T00rT00r"
    
    try:
        # Initialiser l'API
        api = MarsProAPI(email, password)
        await api.login()
        print("✅ Connexion API réussie")
        print(f"👤 User ID: {api.user_id}")
        print()
        
        # PHASE 1: Découverte d'appareils
        print("🔍 PHASE 1: DÉCOUVERTE D'APPAREILS")
        print("=" * 50)
        
        device_data = await api.get_lightdata()
        
        if device_data:
            device_name = device_data.get('deviceName')
            device_id = device_data.get('id')
            pid = device_data.get('device_pid_stable')
            is_bluetooth = device_data.get('isBluetoothDeivice', False)
            is_wifi = device_data.get('isWifiDevice', False)
            
            print(f"📱 Appareil trouvé: {device_name}")
            print(f"🆔 ID: {device_id}")
            print(f"🔑 PID: {pid}")
            print(f"🔵 Bluetooth: {'OUI' if is_bluetooth else 'NON'}")
            print(f"📶 WiFi: {'OUI' if is_wifi else 'NON'}")
            print()
        else:
            print("❌ Aucun appareil trouvé")
            return
        
        # PHASE 2: Détection BLE améliorée
        if is_bluetooth:
            print("🔵 PHASE 2: DÉTECTION BLE AMÉLIORÉE")
            print("=" * 50)
            
            if api.bluetooth_support:
                print("📱 Support Bluetooth BLE disponible")
                
                # Test de la détection améliorée
                detection_success = await api._enhanced_ble_detection()
                
                if detection_success:
                    print(f"✅ Appareil BLE détecté: {api.ble_device.name} ({api.ble_device.address})")
                else:
                    print("❌ Détection BLE échouée - toutes les méthodes essayées")
                    print("💡 L'appareil pourrait être:")
                    print("   • Éteint ou hors de portée")
                    print("   • Pas en mode appairage")
                    print("   • Connecté à un autre appareil")
                    print("   • Pas compatible BLE standard")
            else:
                print("❌ Support Bluetooth BLE non disponible")
                print("💡 Installation requise: pip install bleak")
            print()
        
        # PHASE 3: Test contrôle hybride ultra-robuste
        print("🎛️ PHASE 3: CONTRÔLE HYBRIDE ULTRA-ROBUSTE")
        print("=" * 50)
        
        test_sequences = [
            {"on": True, "pwm": 100, "desc": "🔆 Allumer à 100%", "wait": 4},
            {"on": True, "pwm": 75, "desc": "🔅 Réduire à 75%", "wait": 3},
            {"on": True, "pwm": 50, "desc": "🔅 Réduire à 50%", "wait": 3},
            {"on": True, "pwm": 25, "desc": "🔅 Réduire à 25%", "wait": 3},
            {"on": True, "pwm": 80, "desc": "🔆 Augmenter à 80%", "wait": 3},
            {"on": False, "pwm": 0, "desc": "⚫ Éteindre", "wait": 4}
        ]
        
        for i, test in enumerate(test_sequences, 1):
            print(f"\n🧪 Test {i}: {test['desc']}")
            print("-" * 30)
            
            try:
                success = await api.control_device_hybrid(test['on'], test['pwm'])
                
                if success:
                    print(f"   ✅ {test['desc']} - Commande réussie !")
                    if is_bluetooth and api.ble_device:
                        print("   🔵 Méthode: Bluetooth BLE direct")
                    else:
                        print("   📶 Méthode: API Cloud MarsPro")
                    print("   👀 Vérifiez votre lampe maintenant")
                else:
                    print(f"   ❌ {test['desc']} - Toutes les méthodes ont échoué")
                    
            except Exception as e:
                print(f"   ❌ {test['desc']} - Erreur: {e}")
            
            # Attente entre commandes pour observer
            print(f"   ⏳ Attente {test['wait']} secondes...")
            await asyncio.sleep(test['wait'])
        
        # PHASE 4: Tests de fallback
        print("\n🔄 PHASE 4: TESTS DE FALLBACK")
        print("=" * 50)
        
        print("🧪 Test méthodes legacy...")
        
        # Test set_brightness legacy
        try:
            legacy_response = await api.set_brightness(60)
            if legacy_response and legacy_response.get('code') == '000':
                print("✅ Legacy set_brightness fonctionne")
            else:
                print("❌ Legacy set_brightness échec")
        except Exception as e:
            print(f"❌ Legacy set_brightness erreur: {e}")
        
        await asyncio.sleep(2)
        
        # Test toggle_switch legacy
        try:
            toggle_response = await api.toggle_switch(False, pid)
            if toggle_response and toggle_response.get('code') == '000':
                print("✅ Legacy toggle_switch fonctionne")
            else:
                print("❌ Legacy toggle_switch échec")
        except Exception as e:
            print(f"❌ Legacy toggle_switch erreur: {e}")
        
        # PHASE 5: Diagnostique complet
        print("\n🔍 PHASE 5: DIAGNOSTIQUE COMPLET")
        print("=" * 50)
        
        print("📋 RÉSUMÉ DIAGNOSTIQUE:")
        print(f"   📱 Appareil: {device_name}")
        print(f"   🔑 PID: {pid}")
        print(f"   🔵 Mode Bluetooth: {'OUI' if is_bluetooth else 'NON'}")
        print(f"   📶 Mode WiFi: {'OUI' if is_wifi else 'NON'}")
        
        if is_bluetooth:
            if api.bluetooth_support:
                if hasattr(api, 'ble_device') and api.ble_device:
                    print(f"   📲 Appareil BLE trouvé: {api.ble_device.name}")
                    print("   ✅ Bluetooth BLE opérationnel")
                else:
                    print("   ❌ Appareil BLE non trouvé")
                    print("   💡 Vérifiez que la lampe est allumée et en mode appairage")
            else:
                print("   ❌ Support BLE manquant (pip install bleak)")
        
        print()
        print("🎯 RECOMMANDATIONS POUR HOME ASSISTANT:")
        
        if is_bluetooth:
            print("🔵 APPAREIL BLUETOOTH:")
            print("   1. ✅ L'intégration détecte automatiquement le mode Bluetooth")
            print("   2. 🔄 Elle essaie BLE direct puis fallback cloud")
            print("   3. 📱 Communication locale sans internet si BLE marche")
            print("   4. ☁️ Fallback cloud MarsPro si BLE échoue")
            print("   5. 🏠 Installation: aucun changement requis pour l'utilisateur")
        else:
            print("📶 APPAREIL WIFI:")
            print("   1. ✅ L'intégration utilise l'API cloud MarsPro")
            print("   2. 🌐 Nécessite connexion internet active")
            print("   3. 📡 Activation automatique avant chaque commande")
            print("   4. 🔄 Fallback vers méthodes legacy si échec")
        
        print()
        print("🏁 TEST ULTRA-COMPLET TERMINÉ")
        print("=" * 60)
        print("💡 Si les commandes ont fonctionné, l'intégration HA marchera !")
        
    except Exception as e:
        print(f"❌ Erreur test: {e}")
        import traceback
        traceback.print_exc()

async def test_ble_scan_details():
    """Test détaillé du scan BLE pour debug"""
    print("\n🔍 SCAN BLE DÉTAILLÉ (DEBUG)")
    print("=" * 40)
    
    try:
        from bleak import BleakScanner
        print("✅ Bleak disponible")
        
        print("🔍 Scan de TOUS les appareils BLE (15 secondes)...")
        devices = await BleakScanner.discover(timeout=15.0)
        
        print(f"📱 {len(devices)} appareils BLE trouvés:")
        
        for i, device in enumerate(devices, 1):
            name = device.name or "Sans nom"
            addr = device.address
            rssi = getattr(device, 'rssi', 'N/A')
            
            print(f"   {i:2d}. {name} ({addr}) - Signal: {rssi}")
            
            # Chercher des indices MarsPro
            name_lower = name.lower()
            if any(keyword in name_lower for keyword in ['mars', 'pro', 'mh', 'dim', 'led', 'light']):
                print(f"       ⭐ POTENTIEL MARSPRO: {name}")
        
        print("\n💡 Recherchez votre lampe dans la liste ci-dessus")
        print("💡 Si elle n'apparaît pas:")
        print("   • Vérifiez qu'elle est allumée")
        print("   • Mettez-la en mode appairage (bouton reset ?)")
        print("   • Rapprochez-vous de la lampe")
        
    except ImportError:
        print("❌ Bleak non installé")
        print("💡 Installation: pip install bleak")
    except Exception as e:
        print(f"❌ Erreur scan: {e}")

if __name__ == "__main__":
    asyncio.run(ultra_complete_test())
    asyncio.run(test_ble_scan_details()) 