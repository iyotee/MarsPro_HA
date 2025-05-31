#!/usr/bin/env python3
"""
Test des endpoints MarsPro découverts via l'analyse réseau
Basé sur les captures d'écran montrant mars-pro.api.lgledsolutions.com
"""

import asyncio
import aiohttp
import json
import sys
from typing import Dict, Any, Optional

class MarsPro_RealAPI_Tester:
    def __init__(self):
        self.base_url = "https://mars-pro.api.lgledsolutions.com"
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Headers basés sur l'analyse réseau typique d'applications Android
        self.headers = {
            "User-Agent": "MarsPro/1.0 Android",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate",
        }
        
        # Endpoints découverts dans les captures d'écran
        self.discovered_endpoints = [
            "/api/app/version",
            "/api/android/mine/info/v1",
            "/api/android/udm/getDeviceList/v1", 
            "/api/android/udm/getDeviceDetail/v1"
        ]

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            headers=self.headers,
            timeout=aiohttp.ClientTimeout(total=30)
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def test_endpoint(self, endpoint: str, method: str = "GET", data: Dict = None) -> Dict[str, Any]:
        """Test un endpoint spécifique"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            print(f"\n🔍 Test {method} {url}")
            
            if method.upper() == "POST":
                async with self.session.post(url, json=data) as response:
                    return await self._handle_response(response, url)
            else:
                async with self.session.get(url) as response:
                    return await self._handle_response(response, url)
                    
        except Exception as e:
            print(f"❌ Erreur lors du test de {url}: {str(e)}")
            return {"error": str(e), "url": url}

    async def _handle_response(self, response: aiohttp.ClientResponse, url: str) -> Dict[str, Any]:
        """Traite la réponse HTTP"""
        status = response.status
        
        try:
            # Essaie de parser en JSON
            content = await response.json()
            content_type = "json"
        except:
            # Sinon récupère le texte
            content = await response.text()
            content_type = "text"
        
        result = {
            "url": url,
            "status": status,
            "content_type": content_type,
            "content": content,
            "headers": dict(response.headers)
        }
        
        # Affichage coloré selon le statut
        if status == 200:
            print(f"✅ Status {status} - Succès!")
        elif status in [400, 401, 403]:
            print(f"🔑 Status {status} - Authentification/autorisation requise")
        elif status == 404:
            print(f"❌ Status {status} - Endpoint non trouvé")
        else:
            print(f"⚠️  Status {status} - Réponse inattendue")
        
        # Affiche le contenu si c'est du JSON structuré
        if content_type == "json" and isinstance(content, dict):
            print(f"📄 Contenu JSON:")
            print(json.dumps(content, indent=2, ensure_ascii=False))
        else:
            print(f"📄 Contenu ({len(str(content))} caractères): {str(content)[:200]}...")
        
        return result

    async def test_app_version(self):
        """Test l'endpoint version de l'application"""
        print("\n" + "="*60)
        print("🔍 TEST: Version de l'application")
        print("="*60)
        
        return await self.test_endpoint("/api/app/version", "GET")

    async def test_mine_info(self):
        """Test l'endpoint d'informations utilisateur"""
        print("\n" + "="*60)
        print("🔍 TEST: Informations utilisateur")
        print("="*60)
        
        # Test sans données d'abord
        result = await self.test_endpoint("/api/android/mine/info/v1", "GET")
        
        # Puis test avec POST si GET ne fonctionne pas
        if result.get("status") != 200:
            print("\n🔄 Tentative avec POST...")
            return await self.test_endpoint("/api/android/mine/info/v1", "POST", {})
        
        return result

    async def test_device_list(self):
        """Test l'endpoint de liste des dispositifs"""
        print("\n" + "="*60)
        print("🔍 TEST: Liste des dispositifs")
        print("="*60)
        
        # Test GET d'abord
        result = await self.test_endpoint("/api/android/udm/getDeviceList/v1", "GET")
        
        # Test POST avec données minimales
        if result.get("status") != 200:
            print("\n🔄 Tentative avec POST et données...")
            test_data = {
                "pageNum": 1,
                "pageSize": 20
            }
            return await self.test_endpoint("/api/android/udm/getDeviceList/v1", "POST", test_data)
        
        return result

    async def test_device_detail(self):
        """Test l'endpoint de détails d'un dispositif"""
        print("\n" + "="*60)
        print("🔍 TEST: Détails d'un dispositif")
        print("="*60)
        
        # Test avec un ID de dispositif factice
        test_data = {
            "deviceId": "test123"
        }
        
        return await self.test_endpoint("/api/android/udm/getDeviceDetail/v1", "POST", test_data)

    async def test_login_possibilities(self):
        """Test différentes possibilités de login"""
        print("\n" + "="*60)
        print("🔍 TEST: Endpoints de connexion possibles")
        print("="*60)
        
        # Endpoints de login probables basés sur le pattern observé
        login_endpoints = [
            "/api/android/auth/login",
            "/api/android/auth/login/v1", 
            "/api/android/ulogin/mailLogin/v1",
            "/api/android/user/login",
            "/api/android/user/login/v1"
        ]
        
        results = []
        test_credentials = {
            "email": "test@example.com",
            "password": "testpass123"
        }
        
        for endpoint in login_endpoints:
            print(f"\n🔐 Test endpoint de login: {endpoint}")
            result = await self.test_endpoint(endpoint, "POST", test_credentials)
            results.append(result)
            
            # Petite pause entre les tests
            await asyncio.sleep(1)
        
        return results

    async def run_full_discovery(self):
        """Exécute tous les tests de découverte"""
        print("🚀 DÉMARRAGE DES TESTS MARSPRO API DÉCOUVERTE")
        print("Domaine cible: mars-pro.api.lgledsolutions.com")
        print("Basé sur l'analyse réseau de l'application MarsPro")
        
        results = {}
        
        # Test des endpoints découverts
        results["app_version"] = await self.test_app_version()
        await asyncio.sleep(1)
        
        results["mine_info"] = await self.test_mine_info()
        await asyncio.sleep(1)
        
        results["device_list"] = await self.test_device_list()
        await asyncio.sleep(1)
        
        results["device_detail"] = await self.test_device_detail()
        await asyncio.sleep(1)
        
        results["login_tests"] = await self.test_login_possibilities()
        
        print("\n" + "="*80)
        print("📊 RÉSUMÉ DES DÉCOUVERTES")
        print("="*80)
        
        for test_name, result in results.items():
            if test_name == "login_tests":
                print(f"\n🔐 Tests de connexion:")
                for i, login_result in enumerate(result):
                    status = login_result.get("status", "erreur")
                    url = login_result.get("url", "unknown")
                    print(f"   {i+1}. {url} -> Status {status}")
            else:
                status = result.get("status", "erreur")
                url = result.get("url", "unknown")
                success = "✅" if status == 200 else "❌" if status >= 400 else "⚠️"
                print(f"{success} {test_name}: {url} -> Status {status}")
        
        print("\n💡 CONCLUSIONS:")
        print("- Endpoints fonctionnels (200): Utilisables directement")
        print("- Endpoints 401/403: Nécessitent authentification")
        print("- Endpoints 400: Paramètres requis manquants")
        print("- Endpoints 404: N'existent pas ou chemin incorrect")
        
        return results

async def main():
    """Point d'entrée principal"""
    try:
        async with MarsPro_RealAPI_Tester() as tester:
            results = await tester.run_full_discovery()
            
            # Sauvegarde des résultats
            with open("marspro_discovery_results.json", "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2, ensure_ascii=False, default=str)
            
            print(f"\n💾 Résultats sauvegardés dans: marspro_discovery_results.json")
            
    except KeyboardInterrupt:
        print("\n⏹️  Tests interrompus par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur critique: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 