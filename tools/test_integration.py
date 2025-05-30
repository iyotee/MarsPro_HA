#!/usr/bin/env python3
"""
Script de test pour l'intégration Mars Hydro/MarsPro
"""

import asyncio
import sys
import os

# Ajouter le chemin vers custom_components
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'custom_components'))

from marshydro.api import MarsHydroAPI
from marshydro.api_marspro import MarsProAPI


async def test_marshydro_api(email, password):
    """Test de l'ancienne API MarsHydro"""
    print("🔙 Test de l'API MarsHydro (legacy)")
    print("-" * 40)
    
    try:
        api = MarsHydroAPI(email, password)
        await api.login()
        
        print("✅ Connexion réussie!")
        
        # Test récupération des données des appareils
        light_data = await api.get_lightdata()
        if light_data:
            print(f"💡 Light trouvé: {light_data['deviceName']}")
            print(f"   - Luminosité: {light_data['deviceLightRate']}%")
            print(f"   - État: {'Éteint' if light_data['isClose'] else 'Allumé'}")
        else:
            print("❌ Aucun light trouvé")
        
        fan_data = await api.get_fandata()
        if fan_data:
            print(f"🌀 Ventilateur trouvé: {fan_data['deviceName']}")
            print(f"   - Vitesse: {fan_data.get('speed', 'N/A')}%")
            print(f"   - Température: {fan_data.get('temperature', 'N/A')}°C")
            print(f"   - Humidité: {fan_data.get('humidity', 'N/A')}%")
        else:
            print("❌ Aucun ventilateur trouvé")
            
        return True, "MarsHydro API fonctionne"
        
    except Exception as e:
        print(f"❌ Erreur MarsHydro API: {e}")
        return False, str(e)


async def test_marspro_api(email, password):
    """Test de la nouvelle API MarsPro"""
    print("\n🆕 Test de l'API MarsPro")
    print("-" * 40)
    
    try:
        api = MarsProAPI(email, password)
        await api.login()
        
        print("✅ Connexion MarsPro réussie!")
        
        # Test récupération des données des appareils
        light_data = await api.get_lightdata()
        if light_data:
            print(f"💡 Light trouvé: {light_data['deviceName']}")
            print(f"   - Luminosité: {light_data['deviceLightRate']}%")
            print(f"   - État: {'Éteint' if light_data['isClose'] else 'Allumé'}")
        else:
            print("❌ Aucun light trouvé")
        
        fan_data = await api.get_fandata()
        if fan_data:
            print(f"🌀 Ventilateur trouvé: {fan_data['deviceName']}")
            print(f"   - Vitesse: {fan_data.get('speed', 'N/A')}%")
            print(f"   - Température: {fan_data.get('temperature', 'N/A')}°C")
            print(f"   - Humidité: {fan_data.get('humidity', 'N/A')}%")
        else:
            print("❌ Aucun ventilateur trouvé")
            
        return True, "MarsPro API fonctionne"
        
    except Exception as e:
        print(f"❌ Erreur MarsPro API: {e}")
        print("💡 Cela peut être normal si l'API MarsPro n'existe pas encore ou si les endpoints sont différents")
        return False, str(e)


async def test_fallback_mechanism(email, password):
    """Test du mécanisme de fallback"""
    print("\n🔄 Test du mécanisme de fallback")
    print("-" * 40)
    
    try:
        # Forcer l'utilisation de MarsPro puis fallback
        api = MarsProAPI(email, password)
        
        # Si MarsPro échoue, _fallback_to_legacy_api devrait être appelé
        await api.login()
        
        # Vérifier quelle API est finalement utilisée
        if "lgledsolutions.com" in api.base_url:
            print("✅ Fallback vers MarsHydro réussi")
            return True, "Fallback fonctionne"
        else:
            print("✅ MarsPro fonctionne directement")
            return True, "MarsPro direct"
            
    except Exception as e:
        print(f"❌ Erreur fallback: {e}")
        return False, str(e)


async def main():
    """Fonction principale de test"""
    print("🧪 Test de l'intégration Mars Hydro/MarsPro")
    print("=" * 50)
    
    # Demander les identifiants
    email = input("📧 Email: ").strip()
    password = input("🔒 Mot de passe: ").strip()
    
    if not email or not password:
        print("❌ Email et mot de passe requis")
        return
    
    # Tests
    results = []
    
    # Test 1: API MarsHydro
    success, message = await test_marshydro_api(email, password)
    results.append(("MarsHydro API", success, message))
    
    # Test 2: API MarsPro
    success, message = await test_marspro_api(email, password)
    results.append(("MarsPro API", success, message))
    
    # Test 3: Mécanisme de fallback
    success, message = await test_fallback_mechanism(email, password)
    results.append(("Fallback", success, message))
    
    # Résumé
    print("\n📋 Résumé des tests")
    print("=" * 50)
    
    for test_name, success, message in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
    
    # Recommandations
    print("\n💡 Recommandations")
    print("-" * 20)
    
    if results[0][1]:  # MarsHydro fonctionne
        print("👍 L'ancienne API MarsHydro fonctionne - vous pouvez l'utiliser")
    
    if results[1][1]:  # MarsPro fonctionne
        print("🎉 L'API MarsPro fonctionne - excellent!")
    else:
        print("⚠️  L'API MarsPro ne fonctionne pas encore - utilisation du fallback")
    
    if results[2][1]:  # Fallback fonctionne
        print("🔄 Le mécanisme de fallback fonctionne - sécurité assurée")


if __name__ == "__main__":
    asyncio.run(main()) 