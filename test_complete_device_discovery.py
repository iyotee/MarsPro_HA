#!/usr/bin/env python3
"""
🔍 ANALYSE COMPLÈTE APPAREIL MARSPRO
Diagnostic et configuration WiFi
"""

import asyncio
import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'custom_components', 'marshydro'))

from api_marspro import MarsProAPI

async def analyze_device_complete():
    """Analyse complète de l'appareil et diagnostic"""
    print("🔍 ANALYSE COMPLÈTE APPAREIL MARSPRO")
    print("=" * 60)
    
    email = "jeremy.noverraz2@proton.me"
    password = "T00rT00r"
    
    try:
        api = MarsProAPI(email, password)
        await api.login()
        print("✅ Connecté à l'API MarsPro")
        print(f"👤 User ID: {api.user_id}")
        print()
        
        # Récupérer les informations complètes
        discovery_payload = {
            "currentPage": 1,
            "type": None,
            "deviceProductGroup": 1
        }
        
        devices_response = await api._make_request("/api/android/udm/getDeviceList/v1", discovery_payload)
        
        if not devices_response or not devices_response.get('data'):
            print("❌ Aucun appareil trouvé")
            return
        
        device_list = devices_response['data']['list']
        
        if not device_list:
            print("❌ Liste d'appareils vide")
            return
        
        # Analyser notre appareil
        device = device_list[0]  # Notre lampe
        
        print("📋 INFORMATIONS COMPLÈTES DE L'APPAREIL:")
        print("=" * 50)
        print(f"🆔 ID: {device['id']}")
        print(f"📱 Nom: {device['deviceName']}")
        print(f"🏷️  Type: {device['productType']} (MZL001)")
        print(f"🔢 Serial: {device['deviceSerialnum']}")
        print()
        
        print("🔗 CONFIGURATION RÉSEAU:")
        print("-" * 30)
        print(f"🔵 Bluetooth: {device['isBluetoothDeivice']} (ID: {device['deviceBluetooth']})")
        print(f"📶 WiFi: {device['isWifiDevice']} (Config: {device['deviceWifi']})")
        print(f"🌐 IP: {device['deviceIp']}")
        print(f"📡 Connecté: {device['connectStatus']} (1=connecté)")
        print()
        
        print("⚙️ ÉTAT ACTUEL:")
        print("-" * 30)
        print(f"🔘 Switch: {device['deviceSwitch']} (1=ON)")
        print(f"💡 Luminosité: {device['lightRate']}% (actuelle)")
        print(f"💡 Dernière: {device['lastLightRate']}%")
        print(f"🔒 Fermé: {device['isClose']}")
        print()
        
        print("🔧 INFORMATIONS TECHNIQUES:")
        print("-" * 30)
        device_info = json.loads(device['deviceInfo'])
        print(f"🌍 Timezone: {device_info['timezone']}")
        print(f"🔆 Dernière luminosité: {device_info['lastBright']}%")
        print(f"⏰ Plan activé: {device_info['planEn']}")
        print(f"🏠 Pays: {device['country']}")
        print()
        
        # DIAGNOSTIC PRINCIPAL
        print("🎯 DIAGNOSTIC PRINCIPAL")
        print("=" * 50)
        
        if device['isBluetoothDeivice'] and not device['isWifiDevice']:
            print("🔵 ✅ APPAREIL EN MODE BLUETOOTH SEULEMENT")
            print("📡 ❌ PAS CONFIGURÉ POUR WIFI/CLOUD")
            print()
            print("💡 EXPLICATION DU PROBLÈME:")
            print("   • Votre lampe fonctionne en Bluetooth local")
            print("   • Elle N'ÉCOUTE PAS les commandes cloud")
            print("   • L'app MarsPro utilise Bluetooth direct")
            print("   • Notre API utilise les commandes cloud")
            print()
            print("🔧 SOLUTIONS POSSIBLES:")
            print("   1. 📱 BLUETOOTH DIRECT (recommandé)")
            print("      → Implémenter client BLE dans HA")
            print("      → Communication directe comme l'app")
            print()
            print("   2. 🌐 CONFIGURATION WIFI")
            print("      → Reconfigurer la lampe en WiFi")
            print("      → Puis utiliser commandes cloud")
            print()
            
            # Proposer test Bluetooth direct
            choice = input("🤔 Voulez-vous tester Bluetooth direct ? (o/n): ").strip().lower()
            
            if choice == 'o':
                await test_bluetooth_direct_control(device)
            else:
                await suggest_wifi_configuration(device)
                
        elif device['isWifiDevice']:
            print("📶 ✅ APPAREIL EN MODE WIFI")
            print("🔧 Test des commandes cloud...")
            await test_cloud_control(device)
        else:
            print("❓ Configuration appareil inconnue")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

async def test_bluetooth_direct_control(device):
    """Test du contrôle Bluetooth direct (si bleak disponible)"""
    print("\n🔵 TEST BLUETOOTH DIRECT")
    print("=" * 40)
    
    try:
        from bleak import BleakScanner, BleakClient
        print("✅ Librairie bleak disponible")
        
        print("🔍 Recherche de votre lampe en Bluetooth...")
        
        # Scanner BLE
        devices = await BleakScanner.discover(timeout=10.0)
        
        target_mac = device['deviceBluetooth']  # 345F45EC73CC
        found_device = None
        
        for ble_device in devices:
            if target_mac.lower() in ble_device.address.lower().replace(':', ''):
                found_device = ble_device
                break
            elif target_mac.lower() in (ble_device.name or '').lower():
                found_device = ble_device
                break
        
        if found_device:
            print(f"✅ Lampe trouvée: {found_device.name} ({found_device.address})")
            print("🔧 Tentative de connexion BLE...")
            
            try:
                async with BleakClient(found_device.address) as client:
                    print("✅ Connexion BLE réussie")
                    
                    # Lister les services
                    services = await client.get_services()
                    print(f"📋 {len(services.services)} service(s) trouvé(s)")
                    
                    # Chercher caractéristiques d'écriture
                    write_chars = []
                    for service in services.services:
                        for char in service.characteristics:
                            if "write" in char.properties:
                                write_chars.append(char)
                    
                    if write_chars:
                        print(f"🔧 {len(write_chars)} caractéristique(s) d'écriture")
                        print("💡 CETTE APPROCHE BLUETOOTH DIRECT EST LA SOLUTION")
                        print("   Pour HA, il faudra implémenter un client BLE")
                    else:
                        print("❌ Aucune caractéristique d'écriture")
                        
            except Exception as e:
                print(f"❌ Connexion BLE échouée: {e}")
        else:
            print("❌ Lampe non trouvée en Bluetooth")
            print(f"🔍 Recherché: {target_mac}")
            
    except ImportError:
        print("❌ Librairie bleak non installée")
        print("💡 Pour test Bluetooth: pip install bleak")

async def suggest_wifi_configuration(device):
    """Suggérer configuration WiFi"""
    print("\n🌐 CONFIGURATION WIFI")
    print("=" * 40)
    
    print("💡 Pour utiliser les commandes cloud, il faut configurer WiFi")
    print()
    print("🔧 ÉTAPES CONFIGURATION WIFI:")
    print("   1. Mettre la lampe en mode appairage WiFi")
    print("   2. Utiliser l'app MarsPro officielle")
    print("   3. Aller dans paramètres → WiFi")
    print("   4. Connecter la lampe à votre réseau")
    print("   5. Vérifier qu'elle apparaît comme 'WiFi' dans l'app")
    print()
    print("⚠️  ATTENTION: Une fois en WiFi, le Bluetooth sera désactivé")
    print("🔄 Vous devrez choisir: Bluetooth OU WiFi")

async def test_cloud_control(device):
    """Test des commandes cloud sur appareil WiFi"""
    print("\n☁️ TEST COMMANDES CLOUD")
    print("=" * 40)
    
    email = "jeremy.noverraz2@proton.me"
    password = "T00rT00r"
    
    try:
        api = MarsProAPI(email, password)
        await api.login()
        
        device_id = device['id']
        pid = device['deviceSerialnum']
        
        print(f"🎯 Test sur appareil WiFi {device['deviceName']}")
        
        # Activation
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
            control = {
                "method": "outletCtrl",
                "params": {
                    "pid": pid,
                    "num": 0,
                    "on": 1,
                    "pwm": 75
                }
            }
            
            control_payload = {"data": json.dumps(control)}
            control_response = await api._make_request("/api/upData/device", control_payload)
            
            if control_response and control_response.get('code') == '000':
                print("✅ Commande cloud envoyée")
                print("👀 Votre lampe WiFi devrait réagir")
            else:
                print("❌ Commande cloud échouée")
        else:
            print("❌ Activation cloud échouée")
            
    except Exception as e:
        print(f"❌ Erreur test cloud: {e}")

if __name__ == "__main__":
    asyncio.run(analyze_device_complete()) 