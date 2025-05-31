#!/usr/bin/env python3
"""
🌐 CONFIGURATION WIFI MARSPRO
Convertir appareil Bluetooth → WiFi pour intégration HA optimale
"""

import asyncio
import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'custom_components', 'marshydro'))

from api_marspro import MarsProAPI

async def configure_wifi_mode():
    """Configurer la lampe MarsPro en mode WiFi"""
    print("🌐 CONFIGURATION WIFI MARSPRO")
    print("=" * 50)
    print("🎯 Objectif: Convertir votre lampe Bluetooth → WiFi")
    print("💡 Avantage: Contrôle cloud fiable + compatibilité HA parfaite")
    print()
    
    email = "jeremy.noverraz2@proton.me"
    password = "T00rT00r"
    
    try:
        # Connexion API
        api = MarsProAPI(email, password)
        await api.login()
        print("✅ Connexion MarsPro API réussie")
        print(f"👤 User ID: {api.user_id}")
        print()
        
        # Découverte appareil
        print("🔍 DÉCOUVERTE DE VOTRE APPAREIL")
        print("-" * 40)
        
        device_data = await api.get_lightdata()
        
        if not device_data:
            print("❌ Aucun appareil trouvé")
            return
        
        device_name = device_data.get('deviceName')
        device_id = device_data.get('id')
        pid = device_data.get('device_pid_stable')
        is_bluetooth = device_data.get('isBluetoothDeivice', False)
        is_wifi = device_data.get('isWifiDevice', False)
        
        print(f"📱 Appareil: {device_name}")
        print(f"🆔 ID: {device_id}")
        print(f"🔑 PID: {pid}")
        print(f"🔵 Mode Bluetooth: {'OUI' if is_bluetooth else 'NON'}")
        print(f"📶 Mode WiFi: {'OUI' if is_wifi else 'NON'}")
        print()
        
        # Vérifier si déjà en WiFi
        if is_wifi and not is_bluetooth:
            print("✅ PARFAIT ! Votre appareil est déjà en mode WiFi")
            print("🎯 Test des commandes cloud...")
            
            # Tester directement les commandes cloud
            await test_wifi_cloud_control(api, pid)
            return
        
        elif is_bluetooth:
            print("🔵 APPAREIL EN MODE BLUETOOTH DÉTECTÉ")
            print("💡 Configuration WiFi requise pour optimiser HA")
            print()
            
            # Demander infos WiFi
            print("📋 INFORMATIONS WIFI REQUISES:")
            print("=" * 40)
            
            wifi_ssid = input("🔗 Nom de votre réseau WiFi (SSID): ").strip()
            if not wifi_ssid:
                print("❌ SSID WiFi requis")
                return
            
            wifi_password = input("🔑 Mot de passe WiFi: ").strip()
            if not wifi_password:
                print("❌ Mot de passe WiFi requis")
                return
            
            print()
            print("🚀 DÉMARRAGE CONFIGURATION WIFI")
            print("=" * 40)
            
            # Étape 1: Activation préalable
            print("1️⃣ Activation de l'appareil...")
            activation_success = await activate_device(api)
            
            if activation_success:
                print("   ✅ Appareil activé")
                await asyncio.sleep(2)
            else:
                print("   ⚠️ Activation incertaine, on continue...")
            
            # Étape 2: Configuration WiFi
            print("2️⃣ Configuration WiFi en cours...")
            wifi_success = await configure_device_wifi(api, device_id, device_name, wifi_ssid, wifi_password)
            
            if wifi_success:
                print("   ✅ Configuration WiFi envoyée")
                print("   ⏳ Attente connexion WiFi (20 secondes)...")
                await asyncio.sleep(20)
            else:
                print("   ❌ Configuration WiFi échouée")
                return
            
            # Étape 3: Vérification mode WiFi
            print("3️⃣ Vérification du changement de mode...")
            
            # Re-vérifier l'appareil
            updated_device = await api.get_lightdata()
            if updated_device:
                new_is_wifi = updated_device.get('isWifiDevice', False)
                new_is_bluetooth = updated_device.get('isBluetoothDeivice', False)
                
                print(f"   📶 Mode WiFi: {'OUI' if new_is_wifi else 'NON'}")
                print(f"   🔵 Mode Bluetooth: {'OUI' if new_is_bluetooth else 'NON'}")
                
                if new_is_wifi:
                    print("   🎉 SUCCÈS ! Appareil maintenant en mode WiFi")
                    
                    # Étape 4: Test des commandes WiFi
                    print("4️⃣ Test des commandes WiFi/Cloud...")
                    await test_wifi_cloud_control(api, pid)
                    
                else:
                    print("   ⚠️ Appareil toujours en mode Bluetooth")
                    print("   💡 Vérifiez que:")
                    print("      • La lampe est proche du routeur WiFi")
                    print("      • Le mot de passe WiFi est correct")
                    print("      • Le réseau WiFi est en 2.4GHz (pas 5GHz)")
            else:
                print("   ❌ Impossible de vérifier le statut")
        
        else:
            print("❓ Mode d'appareil non identifié")
        
    except Exception as e:
        print(f"❌ Erreur configuration: {e}")
        import traceback
        traceback.print_exc()

async def activate_device(api):
    """Activer l'appareil avant configuration"""
    try:
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
        
        return response and response.get('code') == '000'
        
    except Exception as e:
        print(f"      Erreur activation: {e}")
        return False

async def configure_device_wifi(api, device_id, device_name, ssid, password):
    """Configurer l'appareil en mode WiFi"""
    try:
        # Format exact de configuration WiFi MarsPro
        wifi_config = {
            "method": "configWiFi",
            "params": {
                "deviceId": str(device_id),
                "ssid": ssid,
                "password": password,
                "deviceName": device_name,
                "userId": str(api.user_id),
                "security": "WPA2",  # Type de sécurité standard
                "hidden": False      # Réseau visible
            }
        }
        
        payload = {"data": json.dumps(wifi_config)}
        response = await api._make_request("/api/upData/device", payload)
        
        print(f"      Réponse WiFi: {response}")
        return response and response.get('code') == '000'
        
    except Exception as e:
        print(f"      Erreur configuration WiFi: {e}")
        return False

async def test_wifi_cloud_control(api, pid):
    """Tester les commandes cloud WiFi"""
    print("\n💡 TEST COMMANDES CLOUD WIFI")
    print("=" * 40)
    
    # Séquence de tests
    test_commands = [
        {"on": True, "pwm": 100, "desc": "Allumer à 100%"},
        {"on": True, "pwm": 50, "desc": "Réduire à 50%"},
        {"on": True, "pwm": 80, "desc": "Augmenter à 80%"},
        {"on": False, "pwm": 0, "desc": "Éteindre"}
    ]
    
    success_count = 0
    
    for i, test in enumerate(test_commands, 1):
        print(f"\n🧪 Test {i}: {test['desc']}")
        
        try:
            # Activation avant chaque commande
            await activate_device(api)
            await asyncio.sleep(1)
            
            # Commande de contrôle
            control = {
                "method": "outletCtrl",
                "params": {
                    "pid": pid,
                    "num": 0,
                    "on": 1 if test['on'] else 0,
                    "pwm": test['pwm']
                }
            }
            
            payload = {"data": json.dumps(control)}
            response = await api._make_request("/api/upData/device", payload)
            
            if response and response.get('code') == '000':
                print(f"   ✅ {test['desc']} - Succès !")
                print("   👀 Vérifiez votre lampe")
                success_count += 1
            else:
                print(f"   ❌ {test['desc']} - Échec: {response}")
                
        except Exception as e:
            print(f"   ❌ {test['desc']} - Erreur: {e}")
        
        await asyncio.sleep(3)
    
    print(f"\n📊 RÉSULTATS: {success_count}/{len(test_commands)} commandes réussies")
    
    if success_count >= 3:
        print("🎉 EXCELLENT ! Contrôle WiFi/Cloud fonctionnel")
        print("✅ Votre lampe est maintenant prête pour Home Assistant")
        print()
        print("🏠 PROCHAINES ÉTAPES POUR HOME ASSISTANT:")
        print("   1. Installer l'intégration MarsPro dans HA")
        print("   2. Configurer avec vos identifiants MarsPro")
        print("   3. L'appareil sera détecté automatiquement en mode WiFi")
        print("   4. Contrôles instantanés et fiables garantis !")
    else:
        print("⚠️ Contrôle WiFi partiellement fonctionnel")
        print("💡 L'intégration HA utilisera les fallbacks automatiques")

if __name__ == "__main__":
    asyncio.run(configure_wifi_mode()) 