#!/usr/bin/env python3
"""
🌐 CONFIGURATION COMPLÈTE LAMPE MARSPRO
Étapes: WiFi → Cloud → Association → Tests
"""

import asyncio
import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'custom_components', 'marshydro'))

from api_marspro import MarsProAPI

async def setup_device_wifi_cloud():
    """Configuration complète de la lampe pour WiFi + Cloud"""
    print("🌐 CONFIGURATION COMPLÈTE LAMPE MARSPRO")
    print("=" * 60)
    print("🎯 Objectif: Connecter la lampe au WiFi et cloud")
    print()
    
    email = "jeremy.noverraz2@proton.me"
    password = "T00rT00r"
    
    try:
        api = MarsProAPI(email, password)
        await api.login()
        print("✅ Connecté à l'API MarsPro")
        print(f"👤 User ID: {api.user_id}")
        print()
        
        # ÉTAPE 1: Découverte/scan des appareils disponibles
        print("🔍 ÉTAPE 1: Découverte des appareils")
        print("-" * 40)
        
        # Scanner les appareils en mode découverte
        discovery_payload = {
            "currentPage": 1,
            "type": None,
            "deviceProductGroup": 1  # On sait que c'est groupe 1
        }
        
        devices = await api._make_request("/api/android/udm/getDeviceList/v1", discovery_payload)
        print(f"📱 Appareils découverts: {json.dumps(devices, indent=2)}")
        
        if not devices or not devices.get('data'):
            print("❌ Aucun appareil trouvé")
            return
        
        # Trouver notre lampe
        our_device = None
        for device in devices['data']:
            if '345F45EC73CC' in device.get('deviceName', ''):
                our_device = device
                break
        
        if not our_device:
            print("❌ Notre lampe non trouvée")
            return
        
        device_id = our_device['id']
        device_name = our_device['deviceName']
        
        print(f"✅ Lampe trouvée: {device_name} (ID: {device_id})")
        print()
        
        # ÉTAPE 2: Configuration WiFi de l'appareil
        print("🌐 ÉTAPE 2: Configuration WiFi")
        print("-" * 40)
        
        # Demander les infos WiFi à l'utilisateur
        print("📋 Configuration WiFi requise:")
        print("   Entrez vos informations WiFi pour connecter la lampe")
        
        wifi_ssid = input("🔗 SSID WiFi (nom du réseau): ").strip()
        wifi_password = input("🔑 Mot de passe WiFi: ").strip()
        
        if not wifi_ssid:
            print("❌ SSID WiFi requis")
            return
        
        # Configuration WiFi de l'appareil
        wifi_config = {
            "method": "configWiFi",
            "params": {
                "deviceId": device_id,
                "ssid": wifi_ssid,
                "password": wifi_password,
                "deviceName": device_name,
                "userId": str(api.user_id)
            }
        }
        
        wifi_payload = {"data": json.dumps(wifi_config)}
        
        print(f"📡 Configuration WiFi en cours...")
        wifi_response = await api._make_request("/api/upData/device", wifi_payload)
        print(f"📤 Réponse WiFi: {wifi_response}")
        
        if wifi_response and wifi_response.get('code') == '000':
            print("✅ Configuration WiFi envoyée")
            print("⏳ Attente 15 secondes (connexion WiFi)...")
            await asyncio.sleep(15)
        else:
            print("⚠️ Configuration WiFi incertaine, on continue...")
            await asyncio.sleep(5)
        
        print()
        
        # ÉTAPE 3: Enregistrement cloud de l'appareil
        print("☁️ ÉTAPE 3: Enregistrement cloud")
        print("-" * 40)
        
        # Enregistrer l'appareil dans le cloud
        cloud_register = {
            "method": "registerDevice",
            "params": {
                "deviceId": device_id,
                "deviceName": device_name,
                "userId": str(api.user_id),
                "deviceType": "LED_DIMMER",  # Type supposé
                "pid": "345F45EC73CC"       # Notre PID
            }
        }
        
        cloud_payload = {"data": json.dumps(cloud_register)}
        
        print(f"☁️ Enregistrement cloud...")
        cloud_response = await api._make_request("/api/upData/device", cloud_payload)
        print(f"📤 Réponse cloud: {cloud_response}")
        
        if cloud_response and cloud_response.get('code') == '000':
            print("✅ Enregistrement cloud réussi")
        else:
            print("⚠️ Enregistrement cloud incertain")
        
        await asyncio.sleep(5)
        print()
        
        # ÉTAPE 4: Association appareil-utilisateur
        print("🔗 ÉTAPE 4: Association appareil-utilisateur")
        print("-" * 40)
        
        # Associer l'appareil à l'utilisateur
        associate = {
            "method": "associateDevice", 
            "params": {
                "deviceId": device_id,
                "userId": str(api.user_id),
                "deviceName": device_name
            }
        }
        
        associate_payload = {"data": json.dumps(associate)}
        
        print(f"🔗 Association utilisateur...")
        associate_response = await api._make_request("/api/upData/device", associate_payload)
        print(f"📤 Réponse association: {associate_response}")
        
        await asyncio.sleep(3)
        print()
        
        # ÉTAPE 5: Activation et test final
        print("🎯 ÉTAPE 5: Activation et test final")
        print("-" * 40)
        
        # Activation de l'appareil (comme dans les captures)
        print("🔧 Activation setDeviceActiveV...")
        
        activation = {
            "method": "setDeviceActiveV",
            "params": {
                "vid": str(api.user_id),
                "unum": "Mars Pro",
                "tOffset": 120
            }
        }
        
        activation_payload = {"data": json.dumps(activation)}
        activation_response = await api._make_request("/api/upData/device", activation_payload)
        print(f"📤 Réponse activation: {activation_response}")
        
        if activation_response and activation_response.get('code') == '000':
            print("✅ Activation réussie")
            
            # Attendre stabilisation
            print("⏳ Attente 10 secondes (stabilisation complète)...")
            await asyncio.sleep(10)
            
            # Test de contrôle final
            print("\n💡 TEST CONTRÔLE FINAL")
            print("-" * 30)
            
            control_tests = [
                {"pwm": 100, "desc": "Test 100%"},
                {"pwm": 50, "desc": "Test 50%"},
                {"pwm": 0, "on": 0, "desc": "Test extinction"}
            ]
            
            for test in control_tests:
                print(f"🔆 {test['desc']}...")
                
                control = {
                    "method": "outletCtrl",
                    "params": {
                        "pid": "345F45EC73CC",
                        "num": 0,
                        "on": test.get('on', 1),
                        "pwm": test['pwm']
                    }
                }
                
                control_payload = {"data": json.dumps(control)}
                control_response = await api._make_request("/api/upData/device", control_payload)
                
                if control_response and control_response.get('code') == '000':
                    print(f"   ✅ {test['desc']} envoyé")
                    print(f"   👀 Lampe devrait maintenant: {test['desc']}")
                else:
                    print(f"   ❌ {test['desc']} échec: {control_response}")
                
                await asyncio.sleep(4)  # Temps pour observer
            
            print("\n" + "=" * 60)
            print("🏁 CONFIGURATION COMPLÈTE TERMINÉE")
            print()
            print("🔍 VÉRIFICATIONS:")
            print("   1. La lampe s'est-elle connectée à votre WiFi ?")
            print("   2. A-t-elle réagi aux tests de contrôle ?")
            print("   3. Les changements de luminosité sont-ils visibles ?")
            print()
            print("✅ Si OUI: La lampe est maintenant configurée pour HA")
            print("❌ Si NON: Problème de configuration réseau/cloud")
            
        else:
            print("❌ Activation échouée")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

async def test_wifi_mode_detection():
    """Tester si la lampe est maintenant en mode WiFi"""
    print("\n🌐 TEST MODE WIFI")
    print("=" * 40)
    
    email = "jeremy.noverraz2@proton.me"
    password = "T00rT00r"
    
    try:
        api = MarsProAPI(email, password)
        await api.login()
        
        # Récupérer les appareils après configuration
        device_data = await api.get_lightdata()
        
        if device_data:
            print(f"📱 Appareil: {device_data.get('deviceName')}")
            print(f"🔗 Type connexion: {device_data.get('connectionType', 'Unknown')}")
            print(f"📡 Statut: {device_data.get('isOnline', 'Unknown')}")
            print(f"🆔 PID: {device_data.get('device_pid_stable', 'N/A')}")
            
            # Vérifier si l'appareil répond maintenant différemment
            if device_data.get('device_pid_stable') != 'N/A':
                print("✅ PID valide trouvé - Mode cloud/WiFi probable")
            else:
                print("⚠️ PID toujours N/A - Peut-être encore en Bluetooth")
        else:
            print("❌ Aucun appareil trouvé après configuration")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    asyncio.run(setup_device_wifi_cloud())
    asyncio.run(test_wifi_mode_detection()) 