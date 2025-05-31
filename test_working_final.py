#!/usr/bin/env python3
"""
🎯 SCRIPT FINAL - Configuration HA MarsPro
Analyse et recommandations pour Home Assistant
"""

import asyncio
import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'custom_components', 'marshydro'))

from api_marspro import MarsProAPI

async def final_analysis():
    """Analyse finale et recommandations pour HA"""
    print("🎯 ANALYSE FINALE MARSPRO POUR HOME ASSISTANT")
    print("=" * 60)
    
    email = "jeremy.noverraz2@proton.me"
    password = "T00rT00r"
    
    try:
        api = MarsProAPI(email, password)
        await api.login()
        print("✅ Connecté à l'API MarsPro")
        print(f"👤 User ID: {api.user_id}")
        print()
        
        # Utiliser la méthode get_lightdata existante
        device_data = await api.get_lightdata()
        
        if not device_data:
            print("❌ Aucun appareil trouvé avec get_lightdata")
            print("🔍 Test découverte directe...")
            
            # Test direct de l'endpoint de découverte
            discovery_response = await api._make_request("/api/android/udm/getDeviceList/v1", {
                "currentPage": 1,
                "type": None,
                "deviceProductGroup": 1
            })
            
            if discovery_response and discovery_response.get('data'):
                devices = discovery_response['data'].get('list', [])
                if devices:
                    device_data = devices[0]
                    print(f"✅ Appareil trouvé via découverte directe")
                else:
                    print("❌ Aucun appareil dans la découverte directe")
                    return
            else:
                print("❌ Échec découverte directe")
                return
        
        # Analyser l'appareil
        print("📋 ANALYSE DE VOTRE APPAREIL MARSPRO")
        print("=" * 50)
        print(f"📱 Nom: {device_data.get('deviceName', 'N/A')}")
        print(f"🆔 ID: {device_data.get('id', 'N/A')}")
        print(f"🔢 Serial/PID: {device_data.get('deviceSerialnum', 'N/A')}")
        print(f"🏷️  Type: {device_data.get('productType', 'N/A')}")
        print()
        
        # Vérifier les modes de connexion
        is_bluetooth = device_data.get('isBluetoothDeivice', False)
        is_wifi = device_data.get('isWifiDevice', False)
        device_wifi = device_data.get('deviceWifi')
        device_ip = device_data.get('deviceIp')
        
        print("🔗 CONFIGURATION RÉSEAU ACTUELLE:")
        print("-" * 40)
        print(f"🔵 Bluetooth: {'✅ OUI' if is_bluetooth else '❌ NON'}")
        print(f"📶 WiFi: {'✅ OUI' if is_wifi else '❌ NON'}")
        print(f"🌐 IP WiFi: {device_ip or 'Aucune'}")
        print(f"📡 Config WiFi: {device_wifi or 'Aucune'}")
        print()
        
        # DIAGNOSTIC ET RECOMMANDATIONS
        print("🎯 DIAGNOSTIC ET RECOMMANDATIONS")
        print("=" * 50)
        
        if is_bluetooth and not is_wifi:
            print("🔵 APPAREIL EN MODE BLUETOOTH SEULEMENT")
            print("=" * 45)
            print()
            print("🔍 PROBLÈME IDENTIFIÉ:")
            print("   • Votre lampe fonctionne uniquement en Bluetooth")
            print("   • Elle N'ÉCOUTE PAS les commandes cloud MarsPro")
            print("   • L'app MarsPro utilise Bluetooth direct")
            print("   • Notre intégration HA utilise l'API cloud")
            print()
            print("💡 SOLUTION RECOMMANDÉE:")
            print("   🔧 IMPLÉMENTER CLIENT BLUETOOTH BLE DANS HA")
            print()
            print("🛠️ ÉTAPES POUR HOME ASSISTANT:")
            print("   1. Modifier l'intégration pour détecter mode Bluetooth")
            print("   2. Ajouter dépendance 'bleak' pour communication BLE")
            print("   3. Scanner et connecter directement à la lampe")
            print("   4. Envoyer commandes via Bluetooth (pas cloud)")
            print()
            print("📝 MODIFICATION DU MANIFEST:")
            print("   Ajouter dans manifest.json:")
            print('   "requirements": ["aiohttp", "bleak"]')
            print()
            print("🔧 MODIFICATION API_MARSPRO.PY:")
            print("   - Détecter si appareil est Bluetooth")
            print("   - Si Bluetooth: utiliser client BLE")
            print("   - Si WiFi: utiliser API cloud")
            print()
            
            # Proposer test Bluetooth
            choice = input("🤔 Voulez-vous tester Bluetooth direct maintenant ? (o/n): ").strip().lower()
            
            if choice == 'o':
                await test_bluetooth_approach(device_data)
            
        elif is_wifi:
            print("📶 APPAREIL EN MODE WIFI")
            print("=" * 30)
            print("✅ Configuration correcte pour l'API cloud")
            print("🧪 Test des commandes cloud...")
            
            # Test activation + contrôle
            await test_cloud_approach(api, device_data)
            
        else:
            print("❓ CONFIGURATION INCONNUE")
            print("⚠️  Appareil ni Bluetooth ni WiFi détecté")
            
        print("\n" + "=" * 60)
        print("🏁 ANALYSE TERMINÉE")
        print()
        print("📋 RÉSUMÉ POUR HOME ASSISTANT:")
        print("   1. Si Bluetooth: Implémenter client BLE")
        print("   2. Si WiFi: L'API cloud devrait marcher")
        print("   3. Tester les deux approches si nécessaire")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

async def test_bluetooth_approach(device_data):
    """Tester l'approche Bluetooth BLE"""
    print("\n🔵 TEST APPROCHE BLUETOOTH BLE")
    print("=" * 45)
    
    try:
        from bleak import BleakScanner
        print("✅ Librairie bleak disponible")
        
        print("🔍 Scan des appareils BLE (10 secondes)...")
        
        devices = await BleakScanner.discover(timeout=10.0)
        
        target_id = device_data.get('deviceBluetooth') or device_data.get('deviceSerialnum')
        
        print(f"🎯 Recherche de: {target_id}")
        print(f"📱 {len(devices)} appareils BLE trouvés")
        
        # Chercher notre lampe
        found = False
        for device in devices:
            device_name = device.name or "Nom inconnu"
            device_addr = device.address
            
            print(f"   📲 {device_name} ({device_addr})")
            
            if target_id and (
                target_id.lower() in device_name.lower() or
                target_id.lower() in device_addr.lower().replace(':', '')
            ):
                print(f"      ✅ LAMPE MARSPRO TROUVÉE !")
                found = True
                
        if found:
            print("\n💡 BLUETOOTH BLE FONCTIONNE !")
            print("🔧 SOLUTION POUR HA:")
            print("   1. Modifier sensor.py pour détecter Bluetooth")
            print("   2. Ajouter BleakClient pour communication")
            print("   3. Reverse engineer le protocole BLE")
            print("   4. Envoyer commandes directement")
        else:
            print("\n❌ Lampe non trouvée en BLE")
            print("💡 Vérifiez que:")
            print("   - La lampe est allumée")
            print("   - Bluetooth PC activé")
            print("   - Lampe en mode appairage")
            
    except ImportError:
        print("❌ bleak non installé")
        print("💡 Installer: pip install bleak")
    except Exception as e:
        print(f"❌ Erreur BLE: {e}")

async def test_cloud_approach(api, device_data):
    """Tester l'approche cloud WiFi"""
    print("\n☁️ TEST APPROCHE CLOUD WIFI")
    print("=" * 40)
    
    device_id = device_data.get('id')
    pid = device_data.get('deviceSerialnum') or device_data.get('device_pid_stable')
    
    try:
        # Test activation
        print("🧪 Test activation setDeviceActiveV...")
        
        activation = {
            "method": "setDeviceActiveV",
            "params": {
                "vid": str(api.user_id),
                "unum": "Mars Pro",
                "tOffset": 120
            }
        }
        
        payload = {"data": json.dumps(activation)}
        response = await api._make_request("/api/upData/device", payload)
        
        if response and response.get('code') == '000':
            print("✅ Activation cloud réussie")
            
            await asyncio.sleep(3)
            
            # Test contrôle
            print("🧪 Test contrôle outletCtrl...")
            
            control = {
                "method": "outletCtrl",
                "params": {
                    "pid": pid,
                    "num": 0,
                    "on": 1,
                    "pwm": 80
                }
            }
            
            control_payload = {"data": json.dumps(control)}
            control_response = await api._make_request("/api/upData/device", control_payload)
            
            if control_response and control_response.get('code') == '000':
                print("✅ Commande cloud envoyée")
                print("👀 Votre lampe WiFi devrait être à 80%")
                print()
                print("💡 L'API CLOUD FONCTIONNE !")
                print("🔧 SOLUTION POUR HA:")
                print("   1. Ajouter setDeviceActiveV avant chaque commande")
                print("   2. L'intégration actuelle devrait marcher")
                print("   3. Tester dans Home Assistant")
            else:
                print("❌ Commande cloud échouée")
                print("⚠️  API cloud ne fonctionne pas correctement")
        else:
            print("❌ Activation cloud échouée")
            
    except Exception as e:
        print(f"❌ Erreur test cloud: {e}")

if __name__ == "__main__":
    asyncio.run(final_analysis()) 