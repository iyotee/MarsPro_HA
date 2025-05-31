#!/usr/bin/env python3
"""
Test final de l'API MarsPro avec les endpoints réels découverts
"""

import asyncio
import sys
import os

# Ajouter le chemin vers le module custom_components
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'custom_components', 'marshydro'))

from api_marspro import MarsProAPI

async def test_marspro_complete():
    """Test complet de l'API MarsPro mise à jour"""
    
    print("🚀 TEST FINAL API MARSPRO")
    print("=" * 50)
    
    # Identifiants de test (à remplacer par de vrais identifiants)
    email = input("📧 Email MarsPro: ").strip()
    password = input("🔑 Mot de passe MarsPro: ").strip()
    
    if not email or not password:
        print("❌ Email et mot de passe requis pour le test")
        return
    
    try:
        # Initialiser l'API MarsPro
        print(f"\n🔧 Initialisation de l'API MarsPro...")
        api = MarsProAPI(email, password)
        
        # Test de connexion
        print(f"\n🔐 Test de connexion...")
        await api.login()
        print(f"✅ Connexion réussie ! Token: {api.token[:20]}...")
        
        # Test récupération données lumières
        print(f"\n💡 Test récupération données lumières...")
        light_data = await api.get_lightdata()
        if light_data:
            print(f"✅ Données lumière récupérées:")
            print(f"   - Nom: {light_data.get('deviceName', 'N/A')}")
            print(f"   - Serial: {light_data.get('deviceSerialnum', 'N/A')}")
            print(f"   - État: {'OFF' if light_data.get('isClose') else 'ON'}")
            print(f"   - Type: {light_data.get('productType', 'N/A')}")
        else:
            print("⚠️  Aucune donnée de lumière trouvée")
        
        # Test récupération données ventilateurs
        print(f"\n🌪️  Test récupération données ventilateurs...")
        fan_data = await api.get_fandata()
        if fan_data:
            print(f"✅ Données ventilateur récupérées:")
            print(f"   - Nom: {fan_data.get('deviceName', 'N/A')}")
            print(f"   - État: {'OFF' if fan_data.get('isClose') else 'ON'}")
        else:
            print("⚠️  Aucune donnée de ventilateur trouvée")
        
        # Test contrôle (si un dispositif est disponible)
        if light_data and light_data.get('deviceSerialnum'):
            print(f"\n🎛️  Test contrôle dispositif...")
            device_id = light_data.get('id') or light_data.get('deviceSerialnum')
            
            # Test allumer/éteindre
            current_state = light_data.get('isClose', False)
            new_state = not current_state
            
            print(f"   État actuel: {'OFF' if current_state else 'ON'}")
            print(f"   Tentative de passage à: {'OFF' if new_state else 'ON'}")
            
            try:
                result = await api.toggle_switch(new_state, device_id)
                if result:
                    print(f"✅ Contrôle réussi!")
                else:
                    print(f"⚠️  Contrôle échoué (peut être normal si le format n'est pas encore correct)")
            except Exception as e:
                print(f"⚠️  Erreur de contrôle: {e}")
        
        print(f"\n🎉 Test terminé avec succès!")
        
    except Exception as e:
        print(f"\n❌ Erreur lors du test: {e}")
        print(f"\n💡 Cela peut indiquer:")
        print(f"   - Identifiants incorrects")
        print(f"   - Format d'authentification à ajuster")
        print(f"   - Endpoints nécessitant des paramètres spécifiques")

async def main():
    """Point d'entrée principal"""
    await test_marspro_complete()

if __name__ == "__main__":
    asyncio.run(main()) 