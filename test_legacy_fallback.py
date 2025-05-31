#!/usr/bin/env python3
"""
Test du fallback vers l'API legacy MarsHydro
Quand MarsPro n'a pas d'appareils configurés
"""

import asyncio
import sys
import os

# Ajouter le path pour importer les APIs
sys.path.append(os.path.join(os.path.dirname(__file__), 'custom_components', 'marshydro'))

try:
    from api_marspro import MarsProAPI
    from api import MarsHydroAPI  # API legacy
except ImportError as e:
    print(f"❌ Impossible d'importer les APIs: {e}")
    print("💡 Assurez-vous d'être dans le répertoire racine du projet")
    sys.exit(1)

class DualAPITester:
    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.marspro_api = MarsProAPI(email, password)
        self.legacy_api = MarsHydroAPI(email, password)
        
    async def test_marspro_first(self):
        """Tester d'abord MarsPro API"""
        print("🎯 TEST MARSPRO API")
        print("=" * 40)
        
        try:
            # Test login MarsPro
            print("🔐 Connexion MarsPro...")
            await self.marspro_api.login()
            print("✅ Login MarsPro réussi !")
            
            # Test récupération appareils MarsPro
            print("📱 Récupération appareils MarsPro...")
            devices = await self.marspro_api.get_all_devices()
            
            if devices:
                print(f"✅ {len(devices)} appareils trouvés dans MarsPro !")
                for i, device in enumerate(devices):
                    name = device.get('deviceName', 'N/A')
                    pid = device.get('deviceSerialnum', 'N/A')
                    print(f"   {i+1}. {name} (PID: {pid})")
                return True, devices
            else:
                print("⚠️  Aucun appareil trouvé dans MarsPro")
                return False, []
                
        except Exception as e:
            print(f"❌ Erreur MarsPro: {e}")
            return False, []
    
    async def test_legacy_fallback(self):
        """Tester l'API legacy en fallback"""
        print("\n🔄 FALLBACK VERS API LEGACY")
        print("=" * 40)
        
        try:
            # Test login Legacy
            print("🔐 Connexion Legacy...")
            await self.legacy_api.login()
            print("✅ Login Legacy réussi !")
            
            # Test récupération données Legacy
            print("💡 Récupération données Legacy...")
            light_data = await self.legacy_api.get_lightdata()
            
            if light_data:
                print("✅ Données d'éclairage trouvées dans Legacy !")
                # Afficher les informations importantes
                if isinstance(light_data, dict):
                    device_id = light_data.get('id', 'N/A')
                    device_name = light_data.get('deviceName', 'N/A')
                    status = "ON" if not light_data.get('isClose', False) else "OFF"
                    print(f"   Appareil: {device_name}")
                    print(f"   ID: {device_id}")
                    print(f"   Status: {status}")
                    
                return True, light_data
            else:
                print("❌ Aucune donnée trouvée dans Legacy")
                return False, None
                
        except Exception as e:
            print(f"❌ Erreur Legacy: {e}")
            return False, None
    
    async def test_dual_control(self, use_legacy=False):
        """Tester le contrôle selon l'API disponible"""
        print(f"\n🎛️  TEST DE CONTRÔLE {'LEGACY' if use_legacy else 'MARSPRO'}")
        print("=" * 40)
        
        try:
            if use_legacy:
                # Test contrôle Legacy
                print("🔆 Test allumage Legacy...")
                await self.legacy_api.toggle_switch(False, None)  # Allumer
                print("✅ Contrôle Legacy réussi !")
                
                await asyncio.sleep(2)
                
                print("🔅 Test extinction Legacy...")
                await self.legacy_api.toggle_switch(True, None)  # Éteindre
                print("✅ Extinction Legacy réussie !")
                
            else:
                # Test contrôle MarsPro (avec PID de test)
                test_pid = "345F45EC73C1"  # PID de test validé
                print(f"🔆 Test contrôle MarsPro (PID: {test_pid})...")
                
                success = await self.marspro_api.control_device_by_pid(test_pid, True, 50)
                if success:
                    print("✅ Contrôle MarsPro réussi !")
                else:
                    print("⚠️  Contrôle MarsPro échoué (normal si PID non lié)")
                
        except Exception as e:
            print(f"❌ Erreur de contrôle: {e}")

async def main():
    """Test principal avec fallback automatique"""
    print("🚀 TEST DUAL API : MARSPRO + LEGACY FALLBACK")
    print("=" * 60)
    
    email = input("📧 Email: ").strip()
    password = input("🔑 Mot de passe: ").strip()
    
    if not email or not password:
        print("❌ Email et mot de passe requis")
        return
    
    tester = DualAPITester(email, password)
    
    try:
        # 1. Tester MarsPro d'abord
        marspro_success, marspro_devices = await tester.test_marspro_first()
        
        # 2. Si MarsPro n'a pas d'appareils, tester Legacy
        if not marspro_success or not marspro_devices:
            print("\n💡 MarsPro sans appareils, test du fallback Legacy...")
            legacy_success, legacy_data = await tester.test_legacy_fallback()
            
            if legacy_success:
                print("\n🎉 Fallback Legacy opérationnel !")
                print("💡 Vous pouvez utiliser l'intégration avec l'API Legacy")
                
                # Test de contrôle Legacy
                test_control = input("\n🎮 Tester le contrôle Legacy ? (y/N): ").strip().lower()
                if test_control in ['y', 'yes', 'oui', 'o']:
                    await tester.test_dual_control(use_legacy=True)
                    
            else:
                print("\n❌ Aucune API ne fonctionne avec ce compte")
                print("💡 Vérifiez vos identifiants et/ou ajoutez des appareils")
        else:
            print("\n🎉 MarsPro opérationnel avec appareils !")
            
            # Test de contrôle MarsPro
            test_control = input("\n🎮 Tester le contrôle MarsPro ? (y/N): ").strip().lower()
            if test_control in ['y', 'yes', 'oui', 'o']:
                await tester.test_dual_control(use_legacy=False)
        
        print(f"\n📋 RÉSUMÉ:")
        print(f"- MarsPro API: {'✅ Fonctionnelle' if marspro_success else '⚠️ Sans appareils'}")
        print(f"- Legacy API: {'✅ Disponible en fallback' if not marspro_success else '💤 Non nécessaire'}")
        
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

async def test_bluetooth_mode():
    """Test du contrôle en mode Bluetooth pur"""
    print("🔵 TEST MODE BLUETOOTH FORCÉ")
    print("=" * 50)
    print("🎯 Test après déconnexion WiFi de la lampe")
    print()
    
    print("📋 INSTRUCTIONS PRÉALABLES:")
    print("1. 📱 Ouvrez l'app MarsPro")
    print("2. ⚙️  Allez dans les paramètres de votre lampe")
    print("3. 📶 DÉCONNECTEZ le WiFi (gardez seulement Bluetooth)")
    print("4. ✅ Confirmez que la lampe est en mode Bluetooth seul")
    print()
    
    response = input("🔍 Avez-vous déconnecté le WiFi de la lampe ? (oui/non): ").lower().strip()
    
    if response != 'oui':
        print("⚠️  Déconnectez d'abord le WiFi puis relancez ce test")
        return False
    
    print()
    print("🚀 Démarrage test mode Bluetooth...")
    
    email = "jeremy.noverraz2@proton.me"
    password = "T00rT00r"
    
    try:
        # Connexion API
        print("🔧 Connexion à l'API MarsPro...")
        api = MarsProAPI(email, password)
        await api.login()
        print("✅ Connecté à l'API MarsPro")
        
        # Vérification que l'appareil est maintenant en mode Bluetooth
        print("\n📱 Vérification du mode de connexion...")
        devices = await api.get_all_devices()
        
        if not devices:
            print("❌ Aucun appareil trouvé")
            return False
        
        device = devices[0]
        device_name = device.get("deviceName")
        is_net_device = device.get("isNetDevice", False)
        is_online = device.get("isOnline", False)
        connection_type = device.get("connection_type", "Unknown")
        
        print(f"📱 Appareil: {device_name}")
        print(f"🔗 Type connexion: {connection_type}")
        print(f"📶 Appareil réseau: {is_net_device}")
        print(f"🌐 En ligne: {is_online}")
        
        if is_net_device:
            print("⚠️  L'appareil est encore détecté comme WiFi")
            print("💡 Attendez quelques minutes ou redémarrez la lampe")
            
            # Test quand même
            print("🧪 Test de contrôle malgré la détection WiFi...")
        else:
            print("✅ L'appareil est maintenant en mode Bluetooth !")
        
        print()
        
        # Tests de contrôle Bluetooth
        stable_pid = device.get("device_pid_stable") or "345F45EC73CC"
        
        test_sequences = [
            (True, 30, "🔆 Test 1: Allumer à 30%"),
            (True, 70, "🔆 Test 2: Augmenter à 70%"),
            (True, 100, "🔆 Test 3: Maximum 100%"),
            (False, 0, "🌙 Test 4: Éteindre"),
            (True, 50, "🔆 Test 5: Rallumer à 50%")
        ]
        
        print("🎛️  TESTS CONTRÔLE MODE BLUETOOTH:")
        print("-" * 40)
        
        all_success = True
        
        for on, pwm, description in test_sequences:
            print(f"\n{description}")
            print(f"   Commande: on={on}, pwm={pwm}")
            
            success = await api.control_device_by_pid(stable_pid, on, pwm)
            
            if success:
                print(f"   ✅ API: Commande envoyée avec succès")
                print(f"   👀 REGARDEZ VOTRE LAMPE MAINTENANT !")
                
                # Demander confirmation visuelle
                await asyncio.sleep(3)
                visual_confirm = input(f"   📋 La lampe a-t-elle réagi ? (oui/non): ").lower().strip()
                
                if visual_confirm == 'oui':
                    print(f"   🎉 SUCCÈS COMPLET ! Contrôle Bluetooth fonctionne !")
                else:
                    print(f"   ❌ Pas de réaction physique")
                    all_success = False
            else:
                print(f"   ❌ API: Commande échouée")
                all_success = False
            
            print(f"   ⏳ Pause 2 secondes...")
            await asyncio.sleep(2)
        
        print(f"\n" + "=" * 50)
        print("🏁 TEST MODE BLUETOOTH TERMINÉ")
        print()
        
        if all_success:
            print("🎊 SUCCÈS TOTAL !")
            print("✅ Le contrôle fonctionne parfaitement en mode Bluetooth")
            print("💡 Solution: Utiliser la lampe en mode Bluetooth uniquement")
            print()
            print("📋 RECOMMANDATIONS:")
            print("   1. Gardez la lampe en mode Bluetooth seul")
            print("   2. L'intégration Home Assistant fonctionnera parfaitement")
            print("   3. Pas besoin de WiFi pour le contrôle")
        else:
            print("⚠️  PROBLÈME PERSISTANT")
            print("❌ Le contrôle ne fonctionne pas même en mode Bluetooth")
            print("💡 Il pourrait y avoir un autre problème")
        
        return all_success
        
    except Exception as e:
        print(f"❌ Erreur dans le test: {e}")
        import traceback
        traceback.print_exc()
        return False

async def explain_wifi_vs_bluetooth():
    """Expliquer la différence WiFi vs Bluetooth"""
    print("\n" + "=" * 60)
    print("💡 EXPLICATION: POURQUOI LE WIFI NE MARCHE PAS")
    print("=" * 60)
    print()
    print("🔍 DÉCOUVERTE IMPORTANTE:")
    print("   Quand la lampe est en WiFi, l'app MarsPro communique")
    print("   DIRECTEMENT avec la lampe en local (pas via le cloud)")
    print()
    print("📡 COMMUNICATION MODES:")
    print("   🔵 Bluetooth: App → Cloud API → Internet → Cloud → Lampe")
    print("                 ↑ INTERCEPTABLE et CONTRÔLABLE")
    print()
    print("   📶 WiFi:      App → Réseau local direct → Lampe")
    print("                 ↑ NON INTERCEPTABLE et NON CONTRÔLABLE via cloud")
    print()
    print("✅ SOLUTION:")
    print("   Utiliser la lampe en mode Bluetooth uniquement")
    print("   L'intégration Home Assistant fonctionnera parfaitement !")

if __name__ == "__main__":
    asyncio.run(main())
    asyncio.run(test_bluetooth_mode())
    asyncio.run(explain_wifi_vs_bluetooth()) 