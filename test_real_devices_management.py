#!/usr/bin/env python3
"""
Script de gestion et test des vrais appareils MarsPro
Interface interactive pour contrôler tous vos appareils
"""

import asyncio
import sys
import os

# Ajouter le path pour importer l'API MarsPro
sys.path.append(os.path.join(os.path.dirname(__file__), 'custom_components', 'marshydro'))

try:
    from api_marspro import MarsProAPI
except ImportError:
    print("❌ Impossible d'importer l'API MarsPro")
    print("💡 Assurez-vous d'être dans le répertoire racine du projet")
    sys.exit(1)

class MarsProDeviceManager:
    def __init__(self, email, password):
        self.api = MarsProAPI(email, password)
        self.devices = []
        
    async def initialize(self):
        """Initialiser la connexion et récupérer les appareils"""
        print("🔐 Connexion à MarsPro...")
        await self.api.login()
        
        print("📱 Récupération de vos appareils...")
        self.devices = await self.api.get_all_devices()
        
        if not self.devices:
            print("❌ Aucun appareil trouvé sur votre compte")
            return False
        
        print(f"✅ Trouvé {len(self.devices)} appareils")
        return True
    
    def display_devices(self):
        """Afficher la liste des appareils"""
        print(f"\n📋 VOS APPAREILS MARSPRO")
        print("=" * 60)
        
        for i, device in enumerate(self.devices):
            name = device.get('deviceName', 'Appareil sans nom')
            pid = device.get('deviceSerialnum', 'PID inconnu')
            status = "🟢 ON" if not device.get('isClose', False) else "🔴 OFF"
            device_type = device.get('productType', 'Type inconnu')
            
            print(f"{i+1:2d}. {name}")
            print(f"    PID: {pid}")
            print(f"    Status: {status}")
            print(f"    Type: {device_type}")
            print()
    
    async def control_device(self, device_index):
        """Contrôler un appareil spécifique"""
        if device_index < 0 or device_index >= len(self.devices):
            print("❌ Index d'appareil invalide")
            return
        
        device = self.devices[device_index]
        name = device.get('deviceName', 'Appareil')
        pid = device.get('deviceSerialnum')
        
        if not pid:
            print("❌ PID non trouvé pour cet appareil")
            return
        
        print(f"\n🎛️  CONTRÔLE DE {name} (PID: {pid})")
        print("=" * 50)
        print("1. Allumer")
        print("2. Éteindre") 
        print("3. Définir luminosité personnalisée")
        print("4. Test séquence luminosité")
        print("0. Retour")
        
        try:
            choice = input("\nVotre choix: ").strip()
            
            if choice == "1":
                # Allumer à 100%
                success = await self.api.control_device_by_pid(pid, True, 100)
                if success:
                    print(f"✅ {name} allumé à 100%")
                else:
                    print(f"❌ Échec allumage de {name}")
                    
            elif choice == "2":
                # Éteindre
                success = await self.api.control_device_by_pid(pid, False, 0)
                if success:
                    print(f"✅ {name} éteint")
                else:
                    print(f"❌ Échec extinction de {name}")
                    
            elif choice == "3":
                # Luminosité personnalisée
                try:
                    brightness = int(input("Luminosité (0-100): ").strip())
                    if 0 <= brightness <= 100:
                        success = await self.api.control_device_by_pid(pid, brightness > 0, brightness)
                        if success:
                            print(f"✅ {name} réglé à {brightness}%")
                        else:
                            print(f"❌ Échec réglage de {name}")
                    else:
                        print("❌ Luminosité doit être entre 0 et 100")
                except ValueError:
                    print("❌ Veuillez entrer un nombre valide")
                    
            elif choice == "4":
                # Test séquence
                print(f"🔄 Test séquence sur {name}...")
                sequence = [10, 30, 50, 80, 100, 50, 20]
                
                for brightness in sequence:
                    print(f"   → {brightness}%")
                    success = await self.api.control_device_by_pid(pid, True, brightness)
                    if success:
                        await asyncio.sleep(2)
                    else:
                        print(f"   ❌ Échec à {brightness}%")
                        break
                
                print("✅ Séquence terminée")
                
            elif choice == "0":
                return
            else:
                print("❌ Choix invalide")
                
        except KeyboardInterrupt:
            print("\n⚠️  Opération annulée")
    
    async def run_interactive_menu(self):
        """Menu principal interactif"""
        while True:
            print(f"\n🏠 GESTIONNAIRE APPAREILS MARSPRO")
            print("=" * 50)
            print("1. Voir tous les appareils")
            print("2. Contrôler un appareil")
            print("3. Actualiser la liste")
            print("4. Test rapide tous appareils")
            print("0. Quitter")
            
            try:
                choice = input("\nVotre choix: ").strip()
                
                if choice == "1":
                    self.display_devices()
                    
                elif choice == "2":
                    if not self.devices:
                        print("❌ Aucun appareil disponible")
                        continue
                    
                    self.display_devices()
                    try:
                        device_num = int(input(f"Numéro appareil (1-{len(self.devices)}): ").strip()) - 1
                        await self.control_device(device_num)
                    except ValueError:
                        print("❌ Veuillez entrer un numéro valide")
                        
                elif choice == "3":
                    print("🔄 Actualisation...")
                    self.devices = await self.api.get_all_devices()
                    print(f"✅ {len(self.devices)} appareils trouvés")
                    
                elif choice == "4":
                    await self.test_all_devices()
                    
                elif choice == "0":
                    print("👋 Au revoir !")
                    break
                    
                else:
                    print("❌ Choix invalide")
                    
            except KeyboardInterrupt:
                print("\n👋 Au revoir !")
                break
            except Exception as e:
                print(f"❌ Erreur: {e}")
    
    async def test_all_devices(self):
        """Test rapide de tous les appareils"""
        if not self.devices:
            print("❌ Aucun appareil à tester")
            return
        
        print(f"\n🧪 TEST RAPIDE DE TOUS LES APPAREILS")
        print("=" * 50)
        
        for i, device in enumerate(self.devices):
            name = device.get('deviceName', f'Appareil {i+1}')
            pid = device.get('deviceSerialnum')
            
            if not pid:
                print(f"❌ {name}: PID manquant")
                continue
            
            print(f"🔍 Test {name} (PID: {pid})...")
            
            # Test simple: allumer à 50%
            success = await self.api.control_device_by_pid(pid, True, 50)
            
            if success:
                print(f"   ✅ {name} répond correctement")
                await asyncio.sleep(1)
            else:
                print(f"   ❌ {name} ne répond pas")
        
        print("🏁 Test terminé")

async def main():
    """Point d'entrée principal"""
    print("🚀 GESTIONNAIRE D'APPAREILS MARSPRO")
    print("=" * 60)
    
    email = input("📧 Email MarsPro: ").strip()
    password = input("🔑 Mot de passe MarsPro: ").strip()
    
    if not email or not password:
        print("❌ Email et mot de passe requis")
        return
    
    manager = MarsProDeviceManager(email, password)
    
    try:
        if await manager.initialize():
            await manager.run_interactive_menu()
        else:
            print("❌ Impossible d'initialiser le gestionnaire")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 