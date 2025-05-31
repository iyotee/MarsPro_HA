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

if __name__ == "__main__":
    asyncio.run(main()) 