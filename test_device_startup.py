#!/usr/bin/env python3
"""
🚀 DÉMARRAGE APPAREIL - Résoudre isStart=0
"""

import asyncio
import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'custom_components', 'marshydro'))

from api_marspro import MarsProAPI

async def start_device():
    """Démarrer l'appareil (isStart: 0 → 1)"""
    print("🚀 DÉMARRAGE APPAREIL")
    print("=" * 50)
    print("🎯 Objectif: Changer isStart de 0 à 1")
    print()
    
    email = "jeremy.noverraz2@proton.me"
    password = "T00rT00r"
    
    try:
        api = MarsProAPI(email, password)
        await api.login()
        
        # Récupérer l'appareil
        light_data = await api.get_lightdata()
        device_id = light_data['id']
        device_serial = light_data['deviceSerialnum']
        
        print(f"📱 Appareil: {light_data['deviceName']}")
        print(f"🆔 ID: {device_id}")
        print(f"🔢 Serial: {device_serial}")
        print()
        
        # 1. Vérifier l'état actuel
        device_list = await api._process_device_list(1)
        if device_list:
            device = device_list[0]
            is_start_before = device.get('isStart', 0)
            print(f"📊 État actuel - isStart: {is_start_before}")
            
            if is_start_before == 1:
                print("✅ Appareil déjà démarré !")
                return True
        
        print()
        
        # 2. Tests de démarrage
        print("🧪 TESTS DE DÉMARRAGE")
        print("-" * 40)
        
        # Test 1: Commande deviceStart
        print("🚀 Test 1: deviceStart...")
        start_payload = {
            "data": json.dumps({
                "method": "deviceStart", 
                "params": {
                    "deviceId": device_id,
                    "deviceSerialnum": device_serial
                }
            })
        }
        result1 = await api._make_request("/api/upData/device", start_payload)
        print(f"📤 Réponse: {result1}")
        await asyncio.sleep(3)
        
        # Test 2: Commande startDevice
        print("🚀 Test 2: startDevice...")
        start_payload2 = {
            "data": json.dumps({
                "method": "startDevice",
                "params": {
                    "pid": device_serial
                }
            })
        }
        result2 = await api._make_request("/api/upData/device", start_payload2)
        print(f"📤 Réponse: {result2}")
        await asyncio.sleep(3)
        
        # Test 3: Commande deviceSwitch (activer le switch)
        print("🔘 Test 3: deviceSwitch ON...")
        switch_payload = {
            "data": json.dumps({
                "method": "deviceSwitch",
                "params": {
                    "deviceId": device_id,
                    "deviceSerialnum": device_serial,
                    "isOn": True,
                    "switch": 1
                }
            })
        }
        result3 = await api._make_request("/api/upData/device", switch_payload)
        print(f"📤 Réponse: {result3}")
        await asyncio.sleep(3)
        
        # Test 4: Activation forcée
        print("⚡ Test 4: Activation forcée...")
        force_payload = {
            "data": json.dumps({
                "method": "outletCtrl",
                "params": {
                    "pid": device_serial,
                    "num": 0,
                    "on": 1,
                    "pwm": 100,
                    "force": True,
                    "activate": True
                }
            })
        }
        result4 = await api._make_request("/api/upData/device", force_payload)
        print(f"📤 Réponse: {result4}")
        await asyncio.sleep(5)
        
        print()
        
        # 3. Vérifier si isStart a changé
        print("🔍 VÉRIFICATION ÉTAT APRÈS DÉMARRAGE")
        print("-" * 40)
        
        device_list_after = await api._process_device_list(1)
        if device_list_after:
            device_after = device_list_after[0]
            is_start_after = device_after.get('isStart', 0)
            device_switch_after = device_after.get('deviceSwitch', 0)
            
            print(f"📊 État après - isStart: {is_start_after}")
            print(f"📊 État après - deviceSwitch: {device_switch_after}")
            
            if is_start_after == 1:
                print("🎉 SUCCÈS ! Appareil démarré !")
                
                # Maintenant tester une commande de contrôle
                print("\n🔆 Test contrôle avec appareil démarré...")
                test_payload = {
                    "data": json.dumps({
                        "method": "outletCtrl",
                        "params": {
                            "pid": device_serial,
                            "num": 0,
                            "on": 1,
                            "pwm": 80
                        }
                    })
                }
                result_test = await api._make_request("/api/upData/device", test_payload)
                print(f"📤 Réponse test: {result_test}")
                print("👀 REGARDEZ VOTRE LAMPE MAINTENANT !")
                
                return True
            else:
                print("❌ isStart toujours à 0")
                
                # Dernière tentative : commande manuelle directe
                print("\n🔧 DERNIÈRE TENTATIVE: Commande manuelle")
                manual_payload = {
                    "deviceId": device_id,
                    "command": "start",
                    "force": True
                }
                result_manual = await api._make_request("/api/android/udm/startDevice/v1", manual_payload)
                print(f"📤 Réponse manuelle: {result_manual}")
        
        print(f"\n💡 SI RIEN NE FONCTIONNE:")
        print(f"   1. Appuyez physiquement sur le bouton de la lampe")
        print(f"   2. Utilisez l'app MarsPro officielle pour démarrer")
        print(f"   3. Débranchez/rebranchez la lampe")
        
        return False
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

async def main():
    success = await start_device()
    
    if success:
        print(f"\n🎊 APPAREIL DÉMARRÉ ! Testez maintenant les commandes normales.")
    else:
        print(f"\n⚠️  Appareil toujours pas démarré. Action manuelle requise.")

if __name__ == "__main__":
    asyncio.run(main()) 