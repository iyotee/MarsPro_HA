#!/usr/bin/env python3
"""
🔵 TEST BLUETOOTH DIRECT
Communication directe avec la lampe via Bluetooth (comme l'app MarsPro)
"""

import asyncio
import subprocess
import re
import json

async def scan_bluetooth_devices():
    """Scanner les appareils Bluetooth disponibles"""
    print("🔵 SCAN BLUETOOTH DIRECT")
    print("=" * 50)
    print("🎯 Recherche de votre lampe MarsPro en Bluetooth direct")
    print()
    
    try:
        # Commande PowerShell pour scanner Bluetooth
        ps_command = """
        Get-PnpDevice -Class Bluetooth | Where-Object {$_.Status -eq "OK"} | 
        Select-Object FriendlyName, InstanceId | ConvertTo-Json
        """
        
        print("🔍 Scan des appareils Bluetooth appairés...")
        result = subprocess.run(
            ["powershell", "-Command", ps_command], 
            capture_output=True, 
            text=True
        )
        
        if result.returncode == 0 and result.stdout.strip():
            try:
                devices = json.loads(result.stdout.strip())
                if not isinstance(devices, list):
                    devices = [devices]
                
                print(f"📱 {len(devices)} appareil(s) Bluetooth trouvé(s):")
                print()
                
                mars_devices = []
                
                for device in devices:
                    name = device.get('FriendlyName', 'N/A')
                    instance_id = device.get('InstanceId', 'N/A')
                    
                    print(f"   📲 {name}")
                    print(f"      ID: {instance_id}")
                    
                    # Chercher des indices MarsPro/LED
                    if any(keyword in name.lower() for keyword in [
                        'mars', 'marspro', 'led', 'light', 'dimbox', 
                        'mh-', '345f45ec73cc', 'hydro'
                    ]):
                        print(f"      ✅ POTENTIEL APPAREIL MARSPRO !")
                        mars_devices.append(device)
                    
                    print()
                
                if mars_devices:
                    print(f"🎉 {len(mars_devices)} appareil(s) MarsPro potentiel(s) trouvé(s) !")
                    return mars_devices
                else:
                    print("⚠️  Aucun appareil MarsPro détecté en Bluetooth")
                    
            except json.JSONDecodeError:
                print("❌ Erreur parsing JSON des appareils Bluetooth")
        else:
            print("❌ Erreur scan PowerShell Bluetooth")
            
    except Exception as e:
        print(f"❌ Erreur scan Bluetooth: {e}")
    
    return []

async def test_bluetooth_communication():
    """Tester la communication Bluetooth directe"""
    print("\n🔵 TEST COMMUNICATION BLUETOOTH DIRECTE")
    print("=" * 50)
    
    # D'abord scanner les appareils
    devices = await scan_bluetooth_devices()
    
    if not devices:
        print("💡 SOLUTIONS:")
        print("1. Vérifiez que la lampe est appairée avec ce PC")
        print("2. Dans Paramètres Windows → Bluetooth, cherchez 'MarsPro' ou 'MH-'")
        print("3. Appairez la lampe si ce n'est pas fait")
        print("4. La lampe doit être en mode appairage")
        return
    
    print("🔧 Pour communication Bluetooth directe, nous aurions besoin de :")
    print("   1. Librairie PyBluez ou bleak")
    print("   2. Scanner les services Bluetooth de la lampe")
    print("   3. Identifier les caractéristiques BLE")
    print("   4. Reverse engineer le protocole de commandes")
    print()
    
    print("🎯 ÉTAPES SUIVANTES:")
    print("   1. Installer: pip install bleak")
    print("   2. Scanner les services BLE de la lampe")
    print("   3. Capturer les commandes BLE de l'app MarsPro")
    print("   4. Implémenter le client BLE direct")

async def explain_bluetooth_vs_cloud():
    """Expliquer pourquoi Bluetooth direct vs cloud"""
    print("\n💡 EXPLICATION: BLUETOOTH DIRECT VS CLOUD")
    print("=" * 60)
    print()
    print("🔍 DÉCOUVERTE PROBABLE:")
    print("   L'app MarsPro utilise 2 modes selon la connexion:")
    print()
    print("🔵 MODE BLUETOOTH DIRECT:")
    print("   📱 App → 🔵 BLE/Bluetooth Direct → 💡 Lampe")
    print("   ↑ Communication locale, instantanée")
    print("   ↑ Fonctionne même sans internet")
    print()
    print("🌐 MODE CLOUD (ce qu'on fait):")
    print("   📱 App → 🌐 API Cloud → 📡 ??? → 💡 Lampe")
    print("   ↑ Pour contrôle à distance")
    print("   ↑ Mais la lampe doit 'écouter' le cloud")
    print()
    print("⚠️  PROBLÈME IDENTIFIÉ:")
    print("   Votre lampe est en mode Bluetooth pur")
    print("   Elle N'ÉCOUTE PAS les commandes cloud")
    print("   Elle n'écoute QUE le Bluetooth direct")
    print()
    print("✅ SOLUTION:")
    print("   Implémenter un client Bluetooth direct")
    print("   Comme le fait l'app MarsPro officielle")

async def check_bluetooth_capability():
    """Vérifier les capacités Bluetooth du PC"""
    print("\n🔧 VÉRIFICATION BLUETOOTH PC")
    print("=" * 50)
    
    try:
        # Vérifier si Bluetooth est activé
        ps_command = "Get-Service bthserv | Select-Object Status"
        result = subprocess.run(
            ["powershell", "-Command", ps_command],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            if "Running" in result.stdout:
                print("✅ Service Bluetooth actif sur ce PC")
            else:
                print("❌ Service Bluetooth inactif")
                print("💡 Activez Bluetooth dans Paramètres Windows")
        
        # Vérifier adaptateur Bluetooth
        ps_command2 = "Get-PnpDevice -Class Bluetooth | Where-Object {$_.Status -eq 'OK'} | Measure-Object"
        result2 = subprocess.run(
            ["powershell", "-Command", ps_command2],
            capture_output=True,
            text=True
        )
        
        if result2.returncode == 0:
            if "Count" in result2.stdout:
                print("✅ Adaptateur Bluetooth détecté")
                print("💡 Votre PC peut communiquer en Bluetooth direct")
            else:
                print("❌ Aucun adaptateur Bluetooth")
                
    except Exception as e:
        print(f"❌ Erreur vérification Bluetooth: {e}")

if __name__ == "__main__":
    asyncio.run(scan_bluetooth_devices())
    asyncio.run(test_bluetooth_communication())
    asyncio.run(explain_bluetooth_vs_cloud())
    asyncio.run(check_bluetooth_capability()) 