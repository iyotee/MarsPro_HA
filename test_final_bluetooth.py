#!/usr/bin/env python3
"""
🎯 TEST FINAL - API MarsPro avec détection Bluetooth automatique
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'custom_components', 'marshydro'))

from api_marspro import MarsProAPI

try:
    from bleak import BleakScanner, BleakClient
    BLEAK_AVAILABLE = True
except ImportError:
    BLEAK_AVAILABLE = False

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

async def test_bluetooth_control():
    """Test du contrôle Bluetooth avec réveil automatique"""
    print("🔋 TEST CONTRÔLE BLUETOOTH FINAL")
    print("=" * 50)
    print("🎯 Test avec réveil automatique avant chaque commande")
    print()
    
    email = "jeremy.noverraz2@proton.me"
    password = "T00rT00r"
    
    try:
        # Connexion API
        print("🔧 Connexion à l'API MarsPro...")
        api = MarsProAPI(email, password)
        await api.login()
        print("✅ Connecté à l'API MarsPro")
        
        # Récupération de l'appareil
        print("\n📱 Recherche de l'appareil...")
        device_data = await api.get_lightdata()
        
        if not device_data:
            print("❌ Aucun appareil trouvé")
            return False
        
        device_name = device_data.get("deviceName")
        stable_pid = device_data.get("device_pid_stable")
        
        print(f"✅ Appareil trouvé: {device_name}")
        print(f"🔑 PID stable: {stable_pid}")
        print(f"🔋 Type: Bluetooth (réveil automatique activé)")
        print()
        
        # Tests de contrôle avec réveil automatique
        test_values = [
            (True, 30, "🔆 Allumer à 30%"),
            (True, 60, "🔆 Allumer à 60%"), 
            (True, 100, "🔆 Allumer à 100%"),
            (True, 10, "🔆 Allumer à 10%"),
            (False, 0, "🌙 Éteindre")
        ]
        
        print("🎛️  Tests de contrôle Bluetooth (avec réveil):")
        print("-" * 50)
        
        for on, pwm, description in test_values:
            print(f"\n{description}")
            print(f"   Commande: on={on}, pwm={pwm}")
            
            # Le contrôle inclut maintenant automatiquement :
            # 1. Réveil Bluetooth
            # 2. Attente stabilisation  
            # 3. Envoi commande
            # 4. Vérification
            # 5. Retry si nécessaire
            
            success = await api.control_device_by_pid(stable_pid, on, pwm)
            
            if success:
                print(f"   ✅ SUCCÈS - Commande Bluetooth envoyée")
                print(f"   💡 La lampe devrait maintenant être {'allumée' if on else 'éteinte'}")
                if on:
                    print(f"   🔆 Luminosité: {pwm}%")
            else:
                print(f"   ❌ ÉCHEC - Commande Bluetooth non envoyée")
            
            # Attente entre commandes pour que la lampe ait le temps de réagir
            print(f"   ⏳ Attente 3 secondes pour observer la lampe...")
            await asyncio.sleep(3)
        
        print("\n" + "=" * 50)
        print("🏁 TEST TERMINÉ")
        print()
        print("🔍 VÉRIFICATION MANUELLE:")
        print("   1. La lampe a-t-elle réagi physiquement ?")
        print("   2. Les changements de luminosité sont-ils visibles ?")
        print("   3. L'allumage/extinction fonctionne-t-il ?")
        print()
        print("⚠️  Si la lampe ne réagit toujours pas :")
        print("   → Problème de connexion Bluetooth")
        print("   → Ou format de commande encore incorrect")
        print("   → Vérifier que l'app MarsPro officielle fonctionne")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur dans le test: {e}")
        import traceback
        traceback.print_exc()
        return False

async def scan_ble_devices():
    """Scanner les appareils BLE (Bluetooth Low Energy)"""
    print("🔵 SCAN BLUETOOTH BLE")
    print("=" * 50)
    
    if not BLEAK_AVAILABLE:
        print("❌ Librairie 'bleak' non installée")
        print("💡 Installez avec: pip install bleak")
        return []
    
    print("🔍 Recherche d'appareils BLE...")
    print("⏱️  Scan de 10 secondes...")
    print()
    
    try:
        devices = await BleakScanner.discover(timeout=10.0)
        
        if not devices:
            print("❌ Aucun appareil BLE trouvé")
            return []
        
        print(f"📱 {len(devices)} appareil(s) BLE trouvé(s):")
        print()
        
        mars_devices = []
        
        for device in devices:
            name = device.name or "Nom inconnu"
            address = device.address
            rssi = device.rssi
            
            print(f"   📲 {name}")
            print(f"      Adresse: {address}")
            print(f"      Signal: {rssi} dBm")
            
            # Chercher des indices MarsPro
            keywords = ['mars', 'marspro', 'mh-', 'dimbox', '345f45ec73cc', 'led', 'light']
            if any(keyword in name.lower() for keyword in keywords):
                print(f"      ✅ POTENTIEL APPAREIL MARSPRO !")
                mars_devices.append(device)
            elif any(keyword in address.lower().replace(':', '') for keyword in ['345f45ec73cc']):
                print(f"      ✅ ADRESSE MAC MATCH MARSPRO !")
                mars_devices.append(device)
            
            print()
        
        if mars_devices:
            print(f"🎉 {len(mars_devices)} appareil(s) MarsPro potentiel(s) !")
            return mars_devices
        else:
            print("⚠️  Aucun appareil MarsPro détecté en BLE")
            print("💡 Votre lampe est peut-être en mode veille")
            print("💡 Ou utilise Bluetooth Classic (pas BLE)")
        
        return []
        
    except Exception as e:
        print(f"❌ Erreur scan BLE: {e}")
        return []

async def analyze_device_services(device):
    """Analyser les services BLE d'un appareil"""
    print(f"\n🔧 ANALYSE SERVICES BLE: {device.name}")
    print("=" * 50)
    
    try:
        async with BleakClient(device.address) as client:
            print(f"✅ Connexion réussie à {device.address}")
            
            # Récupérer tous les services
            services = await client.get_services()
            
            print(f"📋 {len(services.services)} service(s) trouvé(s):")
            print()
            
            for service in services.services:
                print(f"   🔧 Service: {service.uuid}")
                print(f"      Description: {service.description}")
                
                for char in service.characteristics:
                    properties = ', '.join(char.properties)
                    print(f"      📝 Caractéristique: {char.uuid}")
                    print(f"         Propriétés: {properties}")
                    
                    # Si on peut lire, essayer de lire
                    if "read" in char.properties:
                        try:
                            value = await client.read_gatt_char(char.uuid)
                            print(f"         Valeur: {value.hex() if value else 'Vide'}")
                        except Exception:
                            print(f"         Valeur: Lecture échouée")
                
                print()
            
            return services
            
    except Exception as e:
        print(f"❌ Erreur connexion BLE: {e}")
        return None

async def test_marspro_control(device):
    """Tenter de contrôler la lampe via BLE"""
    print(f"\n💡 TEST CONTRÔLE BLE: {device.name}")
    print("=" * 50)
    
    try:
        async with BleakClient(device.address) as client:
            print(f"✅ Connexion établie")
            
            services = await client.get_services()
            
            # Chercher des caractéristiques de contrôle
            control_chars = []
            for service in services.services:
                for char in service.characteristics:
                    if "write" in char.properties:
                        control_chars.append(char)
            
            if not control_chars:
                print("❌ Aucune caractéristique d'écriture trouvée")
                return
            
            print(f"🔧 {len(control_chars)} caractéristique(s) d'écriture trouvée(s)")
            
            # Essayer différentes commandes sur chaque caractéristique
            test_commands = [
                b'\x01\x00\x64',  # Possible: ON, 100%
                b'\x01\x00\x32',  # Possible: ON, 50%
                b'\x00\x00\x00',  # Possible: OFF
                b'\x55\xAA\x01',  # Header possible
                b'\xFF\x01\x64',  # Autre format possible
            ]
            
            for i, char in enumerate(control_chars[:3]):  # Tester max 3 chars
                print(f"\n🧪 Test caractéristique {i+1}: {char.uuid}")
                
                for j, cmd in enumerate(test_commands):
                    print(f"   📤 Commande {j+1}: {cmd.hex()}")
                    try:
                        await client.write_gatt_char(char.uuid, cmd)
                        print(f"      ✅ Envoyée")
                        await asyncio.sleep(1)  # Attendre réaction
                    except Exception as e:
                        print(f"      ❌ Échec: {e}")
                
                print(f"   💡 Regardez si la lampe a réagi !")
                input("   ⏸️  Appuyez sur Entrée pour continuer...")
            
    except Exception as e:
        print(f"❌ Erreur contrôle BLE: {e}")

async def main():
    print("🔵 TEST BLUETOOTH BLE DIRECT - MARSPRO")
    print("=" * 60)
    print()
    
    if not BLEAK_AVAILABLE:
        print("❌ Installation requise:")
        print("   pip install bleak")
        return
    
    # 1. Scanner les appareils BLE
    devices = await scan_ble_devices()
    
    if not devices:
        print("\n💡 SOLUTIONS SI AUCUN APPAREIL:")
        print("   1. Votre lampe doit être allumée")
        print("   2. Bluetooth doit être activé sur PC")
        print("   3. La lampe doit être en mode appairage")
        print("   4. Essayez de redémarrer la lampe")
        print("   5. Votre lampe utilise peut-être Bluetooth Classic")
        return
    
    # 2. Analyser le premier appareil trouvé
    device = devices[0]
    print(f"\n🎯 ANALYSE DE: {device.name} ({device.address})")
    
    services = await analyze_device_services(device)
    
    if services:
        # 3. Tenter le contrôle
        await test_marspro_control(device)
    
    print("\n✅ Test terminé !")
    print("💡 Si la lampe a réagi, on est sur la bonne voie !")

if __name__ == "__main__":
    asyncio.run(main()) 