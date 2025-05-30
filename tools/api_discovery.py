#!/usr/bin/env python3
"""
Script de découverte de l'API MarsPro
Utilise ce script pour identifier les endpoints et structure de l'API MarsPro
"""

import asyncio
import aiohttp
import json
import time
import logging

# Configuration des logs
logging.basicConfig(level=logging.DEBUG)
_LOGGER = logging.getLogger(__name__)

class MarsProDiscovery:
    def __init__(self):
        self.potential_urls = [
            "https://api.marspro.com",
            "https://api.marshydro.com",
            "https://marshydro.lgledsolutions.com",
            "https://marspro.lgledsolutions.com",
            "https://api.lgledsolutions.com/api/marspro",
            "https://cloud.marshydro.com",
            "https://cloud.marspro.com",
            "https://mars-api.com",
            "https://marsapi.com"
        ]
        
        self.potential_endpoints = [
            "/api/auth/login",
            "/api/login",
            "/auth/login",
            "/login",
            "/api/v1/login",
            "/api/v2/login",
            "/marspro/login",
            "/ulogin/mailLogin/v1",  # Ancien endpoint pour comparaison
        ]

    async def test_url_endpoint(self, session, base_url, endpoint, email, password):
        """Test une combinaison URL + endpoint"""
        full_url = f"{base_url}{endpoint}"
        
        # Différents payloads à tester
        payloads = [
            {
                "email": email,
                "password": password,
                "loginMethod": "1",
                "appType": "marspro"
            },
            {
                "email": email,
                "password": password,
                "app": "marspro"
            },
            {
                "username": email,
                "password": password,
                "appType": "marspro"
            },
            {
                "email": email,
                "password": password
            }
        ]
        
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "MarsPro/2.0.0",
            "Accept": "application/json"
        }
        
        for i, payload in enumerate(payloads):
            try:
                _LOGGER.info(f"🧪 Test: {full_url} avec payload {i+1}")
                
                async with session.post(
                    full_url,
                    headers=headers,
                    json=payload,
                    timeout=10
                ) as response:
                    response_text = await response.text()
                    
                    _LOGGER.info(f"✅ Réponse {response.status}: {full_url}")
                    _LOGGER.info(f"📄 Headers: {dict(response.headers)}")
                    _LOGGER.info(f"📝 Body: {response_text[:500]}...")
                    
                    if response.status == 200:
                        try:
                            data = json.loads(response_text)
                            _LOGGER.info(f"🎉 SUCCÈS POTENTIEL: {full_url}")
                            _LOGGER.info(f"🔑 Payload qui fonctionne: {json.dumps(payload, indent=2)}")
                            _LOGGER.info(f"📋 Réponse: {json.dumps(data, indent=2)}")
                            return True, full_url, payload, data
                        except json.JSONDecodeError:
                            _LOGGER.warning(f"⚠️ Réponse 200 mais pas JSON valide")
                    
                    await asyncio.sleep(1)  # Pause entre tests
                    
            except aiohttp.ClientError as e:
                _LOGGER.debug(f"❌ Erreur client {full_url}: {e}")
            except asyncio.TimeoutError:
                _LOGGER.debug(f"⏰ Timeout {full_url}")
            except Exception as e:
                _LOGGER.debug(f"💥 Erreur inattendue {full_url}: {e}")
                
        return False, None, None, None

    async def discover_api(self, email, password):
        """Lance la découverte de l'API MarsPro"""
        _LOGGER.info("🚀 Début de la découverte de l'API MarsPro")
        _LOGGER.info(f"📧 Email de test: {email}")
        
        successful_combinations = []
        
        async with aiohttp.ClientSession() as session:
            for base_url in self.potential_urls:
                _LOGGER.info(f"🌐 Test de l'URL base: {base_url}")
                
                for endpoint in self.potential_endpoints:
                    success, url, payload, response = await self.test_url_endpoint(
                        session, base_url, endpoint, email, password
                    )
                    
                    if success:
                        successful_combinations.append({
                            "url": url,
                            "payload": payload,
                            "response": response
                        })
        
        # Résultats
        if successful_combinations:
            _LOGGER.info("🎉 DÉCOUVERTES RÉUSSIES:")
            for combo in successful_combinations:
                _LOGGER.info(f"✅ URL: {combo['url']}")
                _LOGGER.info(f"📦 Payload: {json.dumps(combo['payload'], indent=2)}")
                _LOGGER.info(f"📋 Réponse: {json.dumps(combo['response'], indent=2)}")
                _LOGGER.info("-" * 50)
        else:
            _LOGGER.warning("❌ Aucune API MarsPro fonctionnelle trouvée")
            _LOGGER.info("💡 Suggestions:")
            _LOGGER.info("  1. Vérifier que les identifiants sont corrects")
            _LOGGER.info("  2. Tester avec l'app MarsPro pour voir si elle fonctionne")
            _LOGGER.info("  3. Analyser le trafic réseau de l'app MarsPro")
            _LOGGER.info("  4. Utiliser l'ancienne API MarsHydro en fallback")

    async def test_legacy_api(self, email, password):
        """Test l'ancienne API pour comparaison"""
        _LOGGER.info("🔙 Test de l'ancienne API MarsHydro pour comparaison")
        
        url = "https://api.lgledsolutions.com/api/android/ulogin/mailLogin/v1"
        payload = {
            "email": email,
            "password": password,
            "loginMethod": "1"
        }
        
        headers = {
            "Content-Type": "application/json",
            "systemData": json.dumps({
                "reqId": int(time.time() * 1000),
                "appVersion": "1.2.0",
                "osType": "android",
                "timestamp": int(time.time())
            })
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, headers=headers, json=payload) as response:
                    data = await response.json()
                    _LOGGER.info(f"🔙 Ancienne API Status: {response.status}")
                    _LOGGER.info(f"🔙 Ancienne API Réponse: {json.dumps(data, indent=2)}")
                    
                    if response.status == 200 and data.get("code") == "000":
                        _LOGGER.info("✅ L'ancienne API fonctionne encore")
                        return True
                    else:
                        _LOGGER.warning("❌ L'ancienne API ne fonctionne pas")
                        return False
            except Exception as e:
                _LOGGER.error(f"💥 Erreur avec l'ancienne API: {e}")
                return False


async def main():
    """Fonction principale"""
    print("🔍 Découverte de l'API MarsPro")
    print("=" * 50)
    
    # Demander les identifiants (remplacer par vos vrais identifiants de test)
    email = input("📧 Email Mars Hydro/MarsPro: ").strip()
    password = input("🔒 Mot de passe: ").strip()
    
    if not email or not password:
        print("❌ Email et mot de passe requis")
        return
    
    discovery = MarsProDiscovery()
    
    # Test de l'ancienne API d'abord
    print("\n🔙 Test de l'ancienne API MarsHydro...")
    legacy_works = await discovery.test_legacy_api(email, password)
    
    # Découverte de la nouvelle API
    print("\n🚀 Recherche de l'API MarsPro...")
    await discovery.discover_api(email, password)
    
    print("\n📋 Résumé:")
    print(f"🔙 Ancienne API MarsHydro: {'✅ Fonctionne' if legacy_works else '❌ Ne fonctionne pas'}")
    print("🆕 Nouvelle API MarsPro: Voir logs ci-dessus")


if __name__ == "__main__":
    asyncio.run(main()) 