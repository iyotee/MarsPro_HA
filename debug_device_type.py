#!/usr/bin/env python3
"""
🔍 DEBUG AVANCÉ - État appareil et test app officielle
"""

import asyncio
import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'custom_components', 'marshydro'))

from api_marspro import MarsProAPI

async def debug_device_state():
    """Analyser l'état complet de l'appareil"""
    print("🔍 DEBUG ÉTAT APPAREIL")
    print("=" * 50)
    
    email = "jeremy.noverraz2@proton.me"
    password = "T00rT00r"
    
    try:
        api = MarsProAPI(email, password)
        await api.login()
        print("✅ Connexion réussie")
        
        # 1. Informations appareil via get_lightdata
        print("\n📱 ÉTAT APPAREIL (get_lightdata):")
        print("-" * 40)
        light_data = await api.get_lightdata()
        
        for key, value in light_data.items():
            if key == 'deviceLightRate' and value == -1:
                print(f"⚠️  {key}: {value} ← PROBLÈME ! Pas d'état luminosité")
            elif key in ['isStart', 'isClose', 'connectStatus']:
                print(f"🔍 {key}: {value}")
            else:
                print(f"📋 {key}: {value}")
        
        device_id = light_data['id']
        device_serial = light_data['deviceSerialnum']
        
        # 2. Détails via getDeviceDetail
        print(f"\n🔎 DÉTAILS COMPLETS (getDeviceDetail):")
        print("-" * 40)
        
        payload = {"deviceId": device_id}
        detail_data = await api._make_request("/api/android/udm/getDeviceDetail/v1", payload)
        
        if detail_data and detail_data.get("code") == "000":
            device_detail = detail_data.get("data", {})
            
            # Vérifier tous les champs critiques
            critical_fields = [
                'isStart', 'isClose', 'connectStatus', 'deviceLightRate',
                'isBluetoothDevice', 'isWifiDevice', 'isNetDevice',
                'deviceStatus', 'deviceSwitch'
            ]
            
            print("🚨 CHAMPS CRITIQUES:")
            for field in critical_fields:
                value = device_detail.get(field, 'MANQUANT')
                if field == 'deviceLightRate' and value == -1:
                    print(f"❌ {field}: {value} ← PROBLÈME MAJEUR !")
                elif field == 'isStart' and value != 1:
                    print(f"⚠️  {field}: {value} ← Appareil pas démarré")
                elif field == 'connectStatus' and value != 1:
                    print(f"⚠️  {field}: {value} ← Problème connexion")
                else:
                    print(f"✅ {field}: {value}")
        
        # 3. Test si l'app MarsPro officielle fonctionne
        print(f"\n❓ QUESTIONS CRUCIALES :")
        print("=" * 50)
        
        print("🔥 1. L'APP MARSPRO OFFICIELLE sur votre téléphone arrive-t-elle à contrôler la lampe ?")
        app_works = input("   Tapez 'oui' si l'app MarsPro contrôle la lampe, 'non' sinon: ").lower().strip()
        
        print("🔌 2. Le bouton physique sur la lampe fonctionne-t-il ?")
        button_works = input("   Tapez 'oui' si le bouton marche, 'non' sinon: ").lower().strip()
        
        print("💡 3. La lampe s'allume-t-elle quand vous la branchez ?")
        power_works = input("   Tapez 'oui' si elle s'allume au branchement, 'non' sinon: ").lower().strip()
        
        # 4. Diagnostic basé sur les réponses
        print(f"\n🔧 DIAGNOSTIC :")
        print("-" * 30)
        
        if app_works == 'non' and button_works == 'non':
            print("💀 PROBLÈME HARDWARE ! La lampe est défectueuse")
            print("🔧 Action: Contacter le support Mars Hydro")
            
        elif app_works == 'non' and button_works == 'oui':
            print("📡 PROBLÈME CONNECTIVITÉ ! La lampe n'est pas vraiment connectée")
            print("🔧 Action: Reset WiFi + reconfiguration complète")
            
        elif app_works == 'oui' and button_works == 'oui':
            print("🎯 PROBLÈME NOTRE API ! L'appareil fonctionne mais pas avec notre code")
            print("🔧 Action: Capturer EXACTEMENT les commandes de l'app qui marche")
            
            # Si l'app officielle marche, capturer ses commandes
            print(f"\n🚨 CAPTURES REQUISES !")
            print("📱 1. Ouvrez HTTP Toolkit")
            print("📱 2. Ouvrez l'app MarsPro")
            print("💡 3. Changez la luminosité dans l'app")
            print("🔍 4. Capturez les requêtes POST vers /api/upData/device")
            print("📋 5. Partagez-moi le payload EXACT qui marche !")
            
        else:
            print("🤔 SITUATION MIXTE - Analyse plus poussée nécessaire")
        
        # 5. Test de commandes alternatives
        if app_works == 'oui':
            print(f"\n🧪 PUISQUE L'APP MARCHE, TESTONS D'AUTRES FORMATS :")
            print("-" * 50)
            
            # Format très simple
            simple_payload = {
                "data": json.dumps({
                    "deviceId": device_id,
                    "brightness": 80
                })
            }
            
            print(f"📝 Test format ultra-simple:")
            print(f"   {json.dumps(simple_payload, indent=2)}")
            result = await api._make_request("/api/upData/device", simple_payload)
            print(f"📤 Réponse: {result}")
            
            await asyncio.sleep(3)
            
            # Format avec serial seulement
            serial_payload = {
                "deviceSerialnum": device_serial,
                "pwm": 90
            }
            
            print(f"📝 Test avec serial direct:")
            print(f"   {json.dumps(serial_payload, indent=2)}")
            result2 = await api._make_request("/api/upData/device", serial_payload)
            print(f"📤 Réponse: {result2}")
        
        return device_detail.get('deviceLightRate', -1) != -1
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

async def main():
    print("🚨 DEBUG COMPLET - RÉSOLVONS CE MYSTÈRE !")
    print("🎯 Objectif: Comprendre pourquoi la lampe ne bouge pas")
    print()
    
    device_ok = await debug_device_state()
    
    print(f"\n🎯 CONCLUSION:")
    print("=" * 40)
    
    if device_ok:
        print("✅ L'appareil semble OK techniquement")
        print("🔧 Le problème est dans notre format de commandes")
    else:
        print("❌ L'appareil a un problème (deviceLightRate = -1)")
        print("🔧 Problème hardware ou connectivité")
    
    print(f"\n📋 ACTIONS REQUISES:")
    print("1. 🧪 Testez l'app MarsPro officielle")
    print("2. 🔍 Si elle marche, capturez ses vraies requêtes")
    print("3. 🔧 Si elle marche pas, reset complet de la lampe")

if __name__ == "__main__":
    asyncio.run(main()) 