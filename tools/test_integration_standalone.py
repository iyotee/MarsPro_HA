#!/usr/bin/env python3
"""
Script de test autonome pour l'intégration Mars Hydro/MarsPro
Ce script peut fonctionner sans Home Assistant installé
"""

import asyncio
import sys
import os
import importlib.util

print("🐛 Debug: Début du script")

# Fonction pour importer directement un module depuis un fichier
def import_module_from_file(module_name, file_path):
    print(f"🐛 Debug: Tentative d'import de {module_name} depuis {file_path}")
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Le fichier {file_path} n'existe pas")
    
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None:
        raise ImportError(f"Impossible de créer une spec pour {module_name}")
    
    module = importlib.util.module_from_spec(spec)
    if module is None:
        raise ImportError(f"Impossible de créer le module {module_name}")
    
    # Injecter les dépendances manquantes si nécessaire
    sys.modules[module_name] = module
    
    try:
        spec.loader.exec_module(module)
        print(f"✅ Module {module_name} importé avec succès")
        return module
    except Exception as e:
        print(f"❌ Erreur lors de l'exécution du module {module_name}: {e}")
        raise

# Obtenir le chemin vers les modules API
base_dir = os.path.join(os.path.dirname(__file__), '..', 'custom_components', 'marshydro')
api_path = os.path.join(base_dir, 'api.py')
api_marspro_path = os.path.join(base_dir, 'api_marspro.py')

print(f"🐛 Debug: Répertoire de base: {base_dir}")
print(f"🐛 Debug: Chemin API: {api_path}")
print(f"🐛 Debug: Chemin API MarsPro: {api_marspro_path}")

# Vérifier l'existence des fichiers
if not os.path.exists(api_path):
    print(f"❌ Fichier manquant: {api_path}")
    sys.exit(1)

if not os.path.exists(api_marspro_path):
    print(f"❌ Fichier manquant: {api_marspro_path}")
    sys.exit(1)

print("✅ Fichiers API trouvés")

# Importer les modules API directement
try:
    print("🔄 Import du module API legacy...")
    api_module = import_module_from_file("api", api_path)
    
    print("🔄 Import du module API MarsPro...")
    api_marspro_module = import_module_from_file("api_marspro", api_marspro_path)
    
    print("🔄 Extraction des classes...")
    MarsHydroAPI = api_module.MarsHydroAPI
    MarsProAPI = api_marspro_module.MarsProAPI
    
    print("✅ Modules API importés avec succès")
    
except Exception as e:
    print(f"❌ Erreur lors de l'importation des modules: {e}")
    import traceback
    traceback.print_exc()
    print("💡 Suggestion: Vérifiez les dépendances (aiohttp) avec: pip install aiohttp")
    sys.exit(1)


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
            print(f"   - ID: {light_data['id']}")
        else:
            print("❌ Aucun light trouvé")
        
        fan_data = await api.get_fandata()
        if fan_data:
            print(f"🌀 Ventilateur trouvé: {fan_data['deviceName']}")
            print(f"   - Vitesse: {fan_data.get('speed', 'N/A')}%")
            print(f"   - Température: {fan_data.get('temperature', 'N/A')}°C")
            print(f"   - Humidité: {fan_data.get('humidity', 'N/A')}%")
            print(f"   - ID: {fan_data['id']}")
        else:
            print("❌ Aucun ventilateur trouvé")
            
        return True, "MarsHydro API fonctionne", {"light": light_data, "fan": fan_data}
        
    except Exception as e:
        print(f"❌ Erreur MarsHydro API: {e}")
        return False, str(e), None


async def test_marspro_api(email, password):
    """Test de la nouvelle API MarsPro"""
    print("\n🆕 Test de l'API MarsPro")
    print("-" * 40)
    
    try:
        api = MarsProAPI(email, password)
        await api.login()
        
        print("✅ Connexion MarsPro réussie!")
        print(f"🌐 URL utilisée: {api.base_url}")
        
        # Test récupération des données des appareils
        light_data = await api.get_lightdata()
        if light_data:
            print(f"💡 Light trouvé: {light_data['deviceName']}")
            print(f"   - Luminosité: {light_data['deviceLightRate']}%")
            print(f"   - État: {'Éteint' if light_data['isClose'] else 'Allumé'}")
            print(f"   - ID: {light_data['id']}")
        else:
            print("❌ Aucun light trouvé")
        
        fan_data = await api.get_fandata()
        if fan_data:
            print(f"🌀 Ventilateur trouvé: {fan_data['deviceName']}")
            print(f"   - Vitesse: {fan_data.get('speed', 'N/A')}%")
            print(f"   - Température: {fan_data.get('temperature', 'N/A')}°C")
            print(f"   - Humidité: {fan_data.get('humidity', 'N/A')}%")
            print(f"   - ID: {fan_data['id']}")
        else:
            print("❌ Aucun ventilateur trouvé")
            
        return True, "MarsPro API fonctionne", {"light": light_data, "fan": fan_data}
        
    except Exception as e:
        print(f"❌ Erreur MarsPro API: {e}")
        print("💡 Cela peut être normal si l'API MarsPro n'existe pas encore ou si les endpoints sont différents")
        return False, str(e), None


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
        print(f"🌐 URL finale utilisée: {api.base_url}")
        
        if "lgledsolutions.com" in api.base_url:
            print("✅ Fallback vers MarsHydro réussi")
            return True, "Fallback fonctionne"
        else:
            print("✅ MarsPro fonctionne directement")
            return True, "MarsPro direct"
            
    except Exception as e:
        print(f"❌ Erreur fallback: {e}")
        return False, str(e)


async def test_device_control(email, password):
    """Test de contrôle des appareils"""
    print("\n🎮 Test de contrôle des appareils")
    print("-" * 40)
    
    try:
        # Utiliser l'API qui fonctionne (priorité à MarsHydro pour les tests)
        api = MarsHydroAPI(email, password)
        await api.login()
        
        # Tester la récupération des appareils
        light_data = await api.get_lightdata()
        fan_data = await api.get_fandata()
        
        if light_data:
            device_id = light_data['id']
            print(f"💡 Test de contrôle du light {light_data['deviceName']}")
            
            # Test toggle (attention: cela va vraiment contrôler l'appareil!)
            response = input("⚠️  Voulez-vous tester le contrôle ON/OFF du light? (y/N): ").lower()
            if response == 'y':
                current_state = light_data['isClose']
                new_state = not current_state
                
                print(f"   🔄 Changement d'état: {'OFF' if new_state else 'ON'}")
                result = await api.toggle_switch(new_state, device_id)
                print(f"   📋 Résultat: {result}")
                
                # Remettre dans l'état initial après 3 secondes
                print("   ⏱️  Remise à l'état initial dans 3 secondes...")
                await asyncio.sleep(3)
                result2 = await api.toggle_switch(current_state, device_id)
                print(f"   📋 Remise à l'état initial: {result2}")
        
        if fan_data:
            device_id = fan_data['id']
            print(f"🌀 Test de contrôle du ventilateur {fan_data['deviceName']}")
            
            response = input("⚠️  Voulez-vous tester le contrôle de vitesse du ventilateur? (y/N): ").lower()
            if response == 'y':
                current_speed = fan_data.get('speed', 50)
                test_speed = 75 if current_speed < 75 else 50
                
                print(f"   🔄 Changement de vitesse: {current_speed}% -> {test_speed}%")
                result = await api.set_fanspeed(test_speed, device_id)
                print(f"   📋 Résultat: {result}")
                
                # Remettre la vitesse initiale après 5 secondes
                print("   ⏱️  Remise à la vitesse initiale dans 5 secondes...")
                await asyncio.sleep(5)
                result2 = await api.set_fanspeed(current_speed, device_id)
                print(f"   📋 Remise à la vitesse initiale: {result2}")
        
        return True, "Tests de contrôle réussis"
        
    except Exception as e:
        print(f"❌ Erreur lors des tests de contrôle: {e}")
        return False, str(e)


async def main():
    """Fonction principale de test"""
    print("🧪 Test autonome de l'intégration Mars Hydro/MarsPro")
    print("=" * 60)
    
    # Demander les identifiants
    email = input("📧 Email Mars Hydro/MarsPro: ").strip()
    password = input("🔒 Mot de passe: ").strip()
    
    if not email or not password:
        print("❌ Email et mot de passe requis")
        return
    
    print(f"\n🔐 Test avec l'email: {email}")
    print("🚀 Début des tests...\n")
    
    # Tests
    results = []
    device_data = {}
    
    # Test 1: API MarsHydro
    success, message, data = await test_marshydro_api(email, password)
    results.append(("MarsHydro API", success, message))
    if data:
        device_data["marshydro"] = data
    
    # Test 2: API MarsPro
    success, message, data = await test_marspro_api(email, password)
    results.append(("MarsPro API", success, message))
    if data:
        device_data["marspro"] = data
    
    # Test 3: Mécanisme de fallback
    success, message = await test_fallback_mechanism(email, password)
    results.append(("Fallback", success, message))
    
    # Test 4: Contrôle des appareils (optionnel)
    if any(result[1] for result in results):  # Si au moins une API fonctionne
        print("\n" + "="*60)
        response = input("🎮 Voulez-vous tester le contrôle des appareils? (y/N): ").lower()
        if response == 'y':
            success, message = await test_device_control(email, password)
            results.append(("Contrôle appareils", success, message))
    
    # Résumé
    print("\n📋 RÉSUMÉ DES TESTS")
    print("=" * 60)
    
    for test_name, success, message in results:
        status = "✅ RÉUSSI" if success else "❌ ÉCHEC"
        print(f"{status:12} {test_name:20} : {message}")
    
    # Recommandations
    print("\n💡 RECOMMANDATIONS")
    print("-" * 30)
    
    if results[0][1]:  # MarsHydro fonctionne
        print("👍 L'ancienne API MarsHydro fonctionne - vous pouvez l'utiliser")
        print("   ⚙️  Configurez Home Assistant avec 'MarsHydro (Ancienne application)'")
    
    if results[1][1]:  # MarsPro fonctionne
        print("🎉 L'API MarsPro fonctionne - excellent!")
        print("   ⚙️  Configurez Home Assistant avec 'MarsPro (Nouvelle application)'")
    else:
        print("⚠️  L'API MarsPro ne fonctionne pas encore")
        print("   🔍 Vous pouvez utiliser tools/api_discovery.py pour découvrir les vrais endpoints")
    
    if results[2][1]:  # Fallback fonctionne
        print("🔄 Le mécanisme de fallback fonctionne - sécurité assurée")
    
    # Données des appareils trouvés
    if device_data:
        print("\n📱 APPAREILS DÉTECTÉS")
        print("-" * 25)
        for api_type, data in device_data.items():
            print(f"\n🔌 Via {api_type.upper()}:")
            if data.get("light"):
                light = data["light"]
                print(f"  💡 {light['deviceName']} (ID: {light['id']})")
            if data.get("fan"):
                fan = data["fan"]
                print(f"  🌀 {fan['deviceName']} (ID: {fan['id']})")
    
    print(f"\n✨ Tests terminés! Vous pouvez maintenant configurer l'intégration dans Home Assistant.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️  Tests interrompus par l'utilisateur")
    except Exception as e:
        print(f"\n💥 Erreur inattendue: {e}")
        import traceback
        traceback.print_exc() 