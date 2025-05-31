#!/usr/bin/env python3
"""
🔍 DIAGNOSTIC TYPE DE CONNEXION APPAREIL
Analyse pourquoi l'appareil n'est pas détecté comme WiFi
"""

import asyncio
import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'custom_components', 'marshydro'))

from api_marspro import MarsProAPI

async def analyze_connection_type():
    """Analyser le type de connexion de l'appareil"""
    print("🔍 DIAGNOSTIC TYPE DE CONNEXION APPAREIL")
    print("=" * 60)
    print("📶 Analyse après connexion WiFi")
    print()
    
    email = "jeremy.noverraz2@proton.me"
    password = "T00rT00r"
    
    try:
        # Connexion API
        print("🔧 Connexion à l'API MarsPro...")
        api = MarsProAPI(email, password)
        await api.login()
        print("✅ Connecté à l'API MarsPro")
        print()
        
        # TEST 1: Recherche exhaustive dans TOUS les groupes
        print("📊 TEST 1: RECHERCHE EXHAUSTIVE GROUPES D'APPAREILS")
        print("-" * 50)
        
        all_devices_found = []
        
        # Tester TOUS les groupes possibles
        groups_to_test = [None, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        
        for group_id in groups_to_test:
            print(f"\n🔍 Test groupe {group_id}...")
            
            payload = {
                "currentPage": 1,
                "type": None,
                "deviceProductGroup": group_id
            }
            
            endpoint = api.endpoints["device_list"]
            data = await api._make_request(endpoint, payload)
            
            if data and data.get('code') == '000':
                devices = data.get('data', {}).get('list', [])
                
                if devices:
                    print(f"   ✅ {len(devices)} appareil(s) dans groupe {group_id}")
                    
                    for device in devices:
                        device_name = device.get("deviceName", "N/A")
                        device_id = device.get("id", "N/A")
                        is_online = device.get("isOnline", False)
                        is_net_device = device.get("isNetDevice", False)
                        
                        print(f"      📱 {device_name} (ID: {device_id})")
                        print(f"         Online: {is_online}")
                        print(f"         Net Device: {is_net_device}")
                        
                        device["found_in_group"] = group_id
                        all_devices_found.append(device)
                else:
                    print(f"   → Aucun appareil dans groupe {group_id}")
            else:
                print(f"   → Erreur groupe {group_id}: {data}")
        
        # Recherche de VOTRE appareil spécifique
        print(f"\n🎯 ANALYSE DE VOTRE APPAREIL: MH-DIMBOX-345F45EC73CC")
        print("-" * 50)
        
        your_device = None
        for device in all_devices_found:
            if "345F45EC73CC" in device.get("deviceName", ""):
                your_device = device
                break
        
        if your_device:
            print(f"✅ Votre appareil trouvé !")
            print(f"📱 Nom: {your_device.get('deviceName')}")
            print(f"🆔 ID: {your_device.get('id')}")
            print(f"📍 Trouvé dans groupe: {your_device.get('found_in_group')}")
            print()
            
            print(f"📋 TOUS LES CHAMPS DE VOTRE APPAREIL:")
            for key, value in sorted(your_device.items()):
                print(f"   {key}: {value}")
            
            print(f"\n🔍 ANALYSE STATUT DE CONNEXION:")
            is_online = your_device.get("isOnline", False)
            is_net_device = your_device.get("isNetDevice", False)
            device_mode = your_device.get("deviceMode", "N/A")
            
            print(f"   En ligne: {is_online}")
            print(f"   Appareil réseau: {is_net_device}")
            print(f"   Mode appareil: {device_mode}")
            
            # Diagnostic du statut
            if is_online and is_net_device:
                print(f"   ✅ STATUT: Appareil WiFi en ligne")
                print(f"   💡 L'appareil est bien connecté au WiFi !")
            elif is_online and not is_net_device:
                print(f"   🔵 STATUT: Appareil Bluetooth en ligne")
                print(f"   ⚠️  L'appareil est en ligne mais pas détecté comme WiFi")
            elif not is_online and is_net_device:
                print(f"   📶 STATUT: Appareil WiFi hors ligne")
                print(f"   ⚠️  Configuré pour WiFi mais pas connecté")
            else:
                print(f"   ❌ STATUT: Appareil Bluetooth hors ligne")
                print(f"   💡 La connexion WiFi n'a peut-être pas abouti")
        else:
            print(f"❌ Votre appareil non trouvé dans aucun groupe !")
        
        # TEST 2: Délai et nouvelle vérification
        print(f"\n⏰ TEST 2: VÉRIFICATION APRÈS DÉLAI")
        print("-" * 50)
        print(f"⏳ Attente 15 secondes pour synchronisation...")
        await asyncio.sleep(15)
        
        print(f"🔄 Nouvelle recherche...")
        updated_devices = await api.get_all_devices()
        
        if updated_devices:
            for device in updated_devices:
                if "345F45EC73CC" in device.get("deviceName", ""):
                    print(f"📊 STATUT ACTUALISÉ:")
                    print(f"   En ligne: {device.get('isOnline')}")
                    print(f"   Appareil réseau: {device.get('isNetDevice')}")
                    print(f"   Type connexion détecté: {device.get('connection_type')}")
                    
                    if device.get('isNetDevice') or device.get('isOnline'):
                        print(f"   ✅ Amélioration détectée !")
                    else:
                        print(f"   ⚠️  Pas de changement")
        
        # TEST 3: Test de connectivité directe
        print(f"\n🌐 TEST 3: TEST COMMANDE AVEC STATUT ACTUEL")
        print("-" * 50)
        
        if your_device:
            device_id = your_device.get("id")
            stable_pid = "345F45EC73CC"
            
            print(f"🎯 Test de commande de contrôle...")
            print(f"   Device ID: {device_id}")
            print(f"   PID: {stable_pid}")
            
            # Test commande simple
            success = await api.control_device_by_pid(stable_pid, True, 50)
            
            if success:
                print(f"   ✅ Commande envoyée avec succès !")
                print(f"   💡 Regardez votre lampe - elle devrait réagir !")
            else:
                print(f"   ❌ Commande échouée")
                print(f"   💡 Cela confirme le problème de connectivité")
        
        # Recommandations
        print(f"\n💡 RECOMMANDATIONS BASÉES SUR L'ANALYSE:")
        print("-" * 50)
        
        if your_device:
            is_online = your_device.get("isOnline", False)
            is_net_device = your_device.get("isNetDevice", False)
            
            if not is_online and not is_net_device:
                print(f"🔧 PROBLÈME: Connexion WiFi non établie")
                print(f"   1. Vérifiez dans l'app MarsPro que le WiFi est bien configuré")
                print(f"   2. Redémarrez la lampe (débranchez/rebranchez)")
                print(f"   3. Refaites la configuration WiFi dans l'app")
            elif is_online and not is_net_device:
                print(f"🤔 PROBLÈME: API détecte Bluetooth malgré WiFi")
                print(f"   1. L'appareil est peut-être en mode hybride")
                print(f"   2. L'API peut utiliser la connexion Bluetooth par défaut")
                print(f"   3. C'est peut-être normal - testons le contrôle")
        
        return your_device is not None
        
    except Exception as e:
        print(f"❌ Erreur dans l'analyse: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(analyze_connection_type()) 