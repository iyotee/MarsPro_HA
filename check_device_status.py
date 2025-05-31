#!/usr/bin/env python3
"""
🔍 VÉRIFICATION ÉTAT APPAREIL - Status détaillé
"""

import asyncio
import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'custom_components', 'marshydro'))

from api_marspro import MarsProAPI

async def check_device_details():
    """Vérifier les détails de l'appareil"""
    print("🔍 VÉRIFICATION ÉTAT DÉTAILLÉ APPAREIL")
    print("=" * 50)
    
    email = "jeremy.noverraz2@proton.me"
    password = "T00rT00r"
    
    try:
        api = MarsProAPI(email, password)
        
        # Connexion
        await api.login()
        print("✅ Connexion réussie\n")
        
        # Récupérer la liste des appareils
        device_list = await api._process_device_list(1)
        
        if device_list:
            device = device_list[0]
            print("📱 DÉTAILS COMPLETS DE L'APPAREIL:")
            print("=" * 40)
            
            # Afficher tous les champs
            for key, value in device.items():
                print(f"  {key}: {value}")
            
            print("\n🔍 ANALYSE DES STATUTS:")
            print("-" * 30)
            
            # Analyser les statuts critiques
            connect_status = device.get("connectStatus")
            is_close = device.get("isClose")
            light_rate = device.get("lastLightRate", device.get("lightRate", device.get("deviceLightRate")))
            is_start = device.get("isStart", 0)
            
            print(f"🌐 Connect Status: {connect_status}")
            if connect_status == 1:
                print("   ✅ Appareil CONNECTÉ")
            elif connect_status == 0:
                print("   ❌ Appareil DÉCONNECTÉ")
            else:
                print(f"   ⚠️  Status inconnu: {connect_status}")
            
            print(f"🔌 Is Close: {is_close}")
            if is_close:
                print("   🔴 Appareil ÉTEINT")
            else:
                print("   🟢 Appareil ALLUMÉ")
            
            print(f"💡 Light Rate: {light_rate}")
            if light_rate == -1:
                print("   ⚠️  Luminosité non définie (-1)")
            elif light_rate == 0:
                print("   🔴 Luminosité à 0%")
            else:
                print(f"   💡 Luminosité à {light_rate}%")
                
            print(f"🚀 Is Start: {is_start}")
            if is_start == 0:
                print("   ⚠️  Appareil pas démarré (isStart=0)")
            else:
                print("   ✅ Appareil démarré")
            
            print("\n💡 RECOMMANDATIONS:")
            print("-" * 20)
            
            if connect_status != 1:
                print("❗ PROBLÈME: Appareil déconnecté du WiFi")
                print("   → Vérifiez la connexion WiFi de votre lampe")
                
            if light_rate == -1:
                print("❗ ATTENTION: Luminosité non définie")
                print("   → La lampe pourrait être en mode veille")
                
            if is_start == 0:
                print("❗ ATTENTION: Appareil pas démarré")
                print("   → Essayez d'allumer manuellement la lampe d'abord")
            
        else:
            print("❌ Aucun appareil trouvé")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")

async def test_get_device_detail():
    """Test de l'endpoint getDeviceDetail que vous avez utilisé"""
    print("\n🔍 TEST GET DEVICE DETAIL (comme votre test)")
    print("=" * 50)
    
    email = "jeremy.noverraz2@proton.me"
    password = "T00rT00r"
    
    try:
        api = MarsProAPI(email, password)
        await api.login()
        
        # Test avec l'endpoint que vous avez utilisé
        payload = {"deviceId": 129209}
        endpoint = "/api/android/udm/getDeviceDetail/v1"
        
        data = await api._make_request(endpoint, payload)
        
        if data:
            print("📤 RÉPONSE DÉTAIL APPAREIL:")
            print(json.dumps(data, indent=2))
            
            if data.get("code") == "000":
                device_data = data.get("data", {})
                
                print(f"\n🔍 STATUTS CRITIQUES:")
                print(f"  connectStatus: {device_data.get('connectStatus')}")
                print(f"  isClose: {device_data.get('isClose')}")
                print(f"  deviceLightRate: {device_data.get('deviceLightRate')}")
                print(f"  isStart: {device_data.get('isStart')}")
                
        else:
            print("❌ Aucune réponse")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")

async def main():
    await check_device_details()
    await test_get_device_detail()

if __name__ == "__main__":
    asyncio.run(main()) 