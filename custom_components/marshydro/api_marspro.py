import aiohttp
import json
import time
import logging
import asyncio

_LOGGER = logging.getLogger(__name__)


class MarsProAPI:
    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.token = None
        # URL réelle découverte lors des tests
        self.base_url = "https://api.lgledsolutions.com/api/marspro"
        self.api_lock = asyncio.Lock()
        self.last_login_time = 0
        self.login_interval = 300  # Minimum interval between logins in seconds
        self.device_id = None

    async def login(self):
        """Authenticate and retrieve the token for MarsPro."""
        async with self.api_lock:
            now = time.time()
            if self.token and (now - self.last_login_time < self.login_interval):
                _LOGGER.info("Token still valid, skipping login.")
                return

            system_data = self._generate_system_data()
            headers = {"systemData": system_data, "Content-Type": "application/json"}
            
            # Essayer différents endpoints découverts
            endpoints_to_try = [
                "/api/auth/login",     # Premier endpoint fonctionnel découvert
                "/api/v2/login",       # Version 2 découverte
                "/api/v1/login",       # Version 1 découverte
                "/ulogin/mailLogin/v1" # Format legacy mais pour MarsPro
            ]
            
            # Payload basé sur les tests de découverte
            payload = {
                "email": self.email,
                "password": self.password,
                "loginMethod": "1",
                "appType": "marspro"  # Paramètre spécifique MarsPro découvert
            }

            async with aiohttp.ClientSession() as session:
                for endpoint in endpoints_to_try:
                    try:
                        full_url = f"{self.base_url}{endpoint}"
                        _LOGGER.info(f"Tentative de connexion MarsPro via {full_url}")
                        
                        async with session.post(
                            full_url,
                            headers=headers,
                            json=payload,
                        ) as response:
                            response.raise_for_status()
                            data = await response.json()
                            _LOGGER.info("MarsPro API Login Response: %s", json.dumps(data, indent=2))
                            
                            # Vérifier si la connexion a réussi
                            if data.get("code") == "000":  # Code de succès supposé
                                # Extraction du token
                                if "data" in data and "token" in data["data"]:
                                    self.token = data["data"]["token"]
                                elif "token" in data:
                                    self.token = data["token"]
                                else:
                                    raise Exception("Token not found in response")
                                    
                                self.last_login_time = now
                                _LOGGER.info("MarsPro login successful, token obtained.")
                                return
                            else:
                                _LOGGER.warning(f"MarsPro login failed with endpoint {endpoint}: {data.get('msg', 'Unknown error')}")
                                continue
                                
                    except aiohttp.ClientError as e:
                        _LOGGER.warning(f"MarsPro login failed with endpoint {endpoint}: {str(e)}")
                        continue
                
                # Si tous les endpoints échouent, essayer le fallback
                _LOGGER.info("All MarsPro endpoints failed, attempting fallback to legacy MarsHydro API...")
                await self._fallback_to_legacy_api()

    async def _fallback_to_legacy_api(self):
        """Fallback to legacy MarsHydro API if MarsPro fails."""
        try:
            # Import absolu au lieu de relatif pour éviter les problèmes
            import sys
            import os
            import importlib.util
            
            # Obtenir le chemin vers le module API legacy
            current_dir = os.path.dirname(__file__)
            api_legacy_path = os.path.join(current_dir, 'api.py')
            
            # Charger le module legacy
            spec = importlib.util.spec_from_file_location("legacy_api", api_legacy_path)
            legacy_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(legacy_module)
            
            # Créer une instance de l'API legacy
            legacy_api = legacy_module.MarsHydroAPI(self.email, self.password)
            await legacy_api.login()
            
            # Copier les données importantes
            self.token = legacy_api.token
            self.base_url = legacy_api.base_url
            
            _LOGGER.info("Fallback to legacy API successful")
            
        except Exception as e:
            _LOGGER.error(f"Fallback to legacy API failed: {e}")
            raise Exception(f"Both MarsPro and legacy MarsHydro APIs failed. MarsPro: No valid credentials, Legacy: {e}")

    async def safe_api_call(self, func, *args, **kwargs):
        """Ensure thread-safe API calls."""
        async with self.api_lock:
            return await func(*args, **kwargs)

    async def _ensure_token(self):
        """Ensure that the token is valid."""
        if not self.token:
            await self.login()

    async def toggle_switch(self, is_close: bool, device_id: str):
        """Toggle the light or fan switch (on/off) - MarsPro version."""
        await self._ensure_token()

        system_data = self._generate_system_data()
        headers = {
            "systemData": system_data,
            "Content-Type": "application/json",
        }
        
        # Payload adapté pour MarsPro
        payload = {
            "isClose": is_close,
            "deviceId": device_id,
            "groupId": None
        }

        _LOGGER.debug(f"MarsPro toggle switch payload: {json.dumps(payload, indent=2)}")

        # Essayer différents endpoints de contrôle
        control_endpoints = [
            "/udm/lampSwitch/v1",  # Endpoint legacy adapté
            "/device/control",      # Endpoint hypothétique
            "/api/device/control"   # Endpoint avec préfixe API
        ]

        async with aiohttp.ClientSession() as session:
            for endpoint in control_endpoints:
                try:
                    full_url = f"{self.base_url}{endpoint}"
                    async with session.post(
                        full_url,
                        headers=headers, 
                        json=payload
                    ) as response:
                        response_json = await response.json()
                        _LOGGER.info(
                            "MarsPro Toggle Switch Response: %s",
                            json.dumps(response_json, indent=2),
                        )
                        
                        # Gestion des codes d'erreur MarsPro
                        if response_json.get("code") == "102" or response_json.get("status") == "unauthorized":
                            _LOGGER.warning("Token expired, re-authenticating...")
                            await self.login()
                            return await self.toggle_switch(is_close, device_id)
                        
                        if response_json.get("code") == "000":  # Succès
                            return response_json
                        else:
                            _LOGGER.warning(f"Control failed with endpoint {endpoint}: {response_json.get('msg', 'Unknown error')}")
                            continue
                            
                except Exception as e:
                    _LOGGER.warning(f"Control failed with endpoint {endpoint}: {e}")
                    continue
            
            # Si aucun endpoint ne fonctionne, retourner une erreur
            raise Exception("All MarsPro control endpoints failed")

    async def _process_device_list(self, product_type):
        """Retrieve device list for a given product type - MarsPro version."""
        await self._ensure_token()
        system_data = self._generate_system_data()
        headers = {
            "Accept-Encoding": "gzip",
            "Content-Type": "application/json",
            "Host": "api.lgledsolutions.com",
            "User-Agent": "MarsPro/2.0.0",
            "systemData": system_data,
        }
        
        # Payload adapté pour MarsPro
        payload = {
            "currentPage": 0, 
            "type": None, 
            "productType": product_type
        }

        # Essayer différents endpoints de liste d'appareils
        list_endpoints = [
            "/udm/getDeviceList/v1",  # Endpoint legacy adapté
            "/device/list",           # Endpoint hypothétique
            "/api/device/list"        # Endpoint avec préfixe API
        ]

        async with aiohttp.ClientSession() as session:
            for endpoint in list_endpoints:
                try:
                    full_url = f"{self.base_url}{endpoint}"
                    async with session.post(
                        full_url,
                        headers=headers, 
                        json=payload
                    ) as response:
                        response_json = await response.json()
                        
                        # Structure de réponse MarsPro
                        if response_json.get("code") == "000":
                            device_list = response_json.get("data", {}).get("devices", []) or response_json.get("data", {}).get("list", [])
                            return device_list
                        else:
                            _LOGGER.warning(f"Device list failed with endpoint {endpoint}: {response_json.get('msg', 'Unknown error')}")
                            continue
                            
                except Exception as e:
                    _LOGGER.warning(f"Device list failed with endpoint {endpoint}: {e}")
                    continue
            
            _LOGGER.error("All MarsPro device list endpoints failed")
            return []

    async def get_lightdata(self):
        """Retrieve light data from the MarsPro API."""
        device_list = await self._process_device_list("LIGHT")
        if device_list:
            device_data = device_list[0]
            self.device_id = device_data.get("id") or device_data.get("deviceId")
            return {
                "deviceName": device_data.get("deviceName") or device_data.get("name"),
                "deviceLightRate": device_data.get("deviceLightRate") or device_data.get("brightness"),
                "isClose": device_data.get("isClose") or device_data.get("isOff"),
                "id": self.device_id,
                "deviceImage": device_data.get("deviceImg") or device_data.get("image"),
            }
        else:
            _LOGGER.warning("No light devices found in MarsPro.")
            return None

    async def get_fandata(self):
        """Retrieve fan data from the MarsPro API."""
        device_list = await self._process_device_list("WIND")
        if device_list:
            device_data = device_list[0]
            _LOGGER.debug("MarsPro fan data retrieved: %s", json.dumps(device_data, indent=2))
            return {
                "deviceName": device_data.get("deviceName") or device_data.get("name"),
                "deviceLightRate": device_data.get("deviceLightRate") or device_data.get("speed"),
                "humidity": device_data.get("humidity"),
                "temperature": device_data.get("temperature"),
                "speed": device_data.get("speed"),
                "isClose": device_data.get("isClose") or device_data.get("isOff"),
                "id": device_data.get("id") or device_data.get("deviceId"),
                "deviceImage": device_data.get("deviceImg") or device_data.get("image"),
            }
        else:
            _LOGGER.warning("No fan devices found in MarsPro.")
            return None

    async def set_brightness(self, brightness):
        """Set the brightness of the MarsPro light."""
        await self._ensure_token()

        if not self.device_id:
            device_data = await self.get_lightdata()
            if device_data:
                self.device_id = device_data.get("id")

        system_data = self._generate_system_data()
        headers = {
            "Accept-Encoding": "gzip",
            "Content-Type": "application/json",
            "Host": "api.lgledsolutions.com",
            "systemData": system_data,
            "User-Agent": "MarsPro/2.0.0",
        }
        
        # Payload adapté pour MarsPro
        payload = {
            "deviceLightRate": brightness,
            "deviceId": self.device_id,
            "groupId": None
        }

        # Essayer différents endpoints de luminosité
        brightness_endpoints = [
            "/udm/adjustLight/v1",    # Endpoint legacy adapté
            "/device/setBrightness",  # Endpoint hypothétique
            "/api/device/setBrightness"  # Endpoint avec préfixe API
        ]

        async with aiohttp.ClientSession() as session:
            for endpoint in brightness_endpoints:
                try:
                    full_url = f"{self.base_url}{endpoint}"
                    async with session.post(
                        full_url,
                        headers=headers, 
                        json=payload
                    ) as response:
                        response_json = await response.json()
                        _LOGGER.info(
                            "MarsPro Set Brightness Response: %s",
                            json.dumps(response_json, indent=2),
                        )
                        
                        if response_json.get("code") == "000":  # Succès
                            return response_json
                        else:
                            _LOGGER.warning(f"Brightness control failed with endpoint {endpoint}: {response_json.get('msg', 'Unknown error')}")
                            continue
                            
                except Exception as e:
                    _LOGGER.warning(f"Brightness control failed with endpoint {endpoint}: {e}")
                    continue
            
            raise Exception("All MarsPro brightness control endpoints failed")

    async def set_fanspeed(self, speed, fan_device_id):
        """Set the speed of the MarsPro fan."""
        await self._ensure_token()

        system_data = self._generate_system_data()
        headers = {
            "Accept-Encoding": "gzip",
            "Content-Type": "application/json",
            "Host": "api.lgledsolutions.com",
            "systemData": system_data,
            "User-Agent": "MarsPro/2.0.0",
        }
        
        # Payload adapté pour MarsPro
        payload = {
            "deviceLightRate": speed,  # Utiliser le même paramètre que pour la luminosité
            "deviceId": fan_device_id,
            "groupId": None
        }

        _LOGGER.debug(f"MarsPro fan speed payload: {json.dumps(payload, indent=2)}")

        # Utiliser le même endpoint que pour la luminosité (pattern découvert)
        speed_endpoints = [
            "/udm/adjustLight/v1",    # Endpoint legacy adapté
            "/device/setFanSpeed",    # Endpoint hypothétique
            "/api/device/setFanSpeed" # Endpoint avec préfixe API
        ]

        async with aiohttp.ClientSession() as session:
            for endpoint in speed_endpoints:
                try:
                    full_url = f"{self.base_url}{endpoint}"
                    async with session.post(
                        full_url,
                        headers=headers, 
                        json=payload
                    ) as response:
                        response_json = await response.json()
                        _LOGGER.info(
                            "MarsPro Set Fan Speed Response: %s",
                            json.dumps(response_json, indent=2),
                        )
                        
                        if response_json.get("code") == "000":  # Succès
                            return response_json
                        else:
                            _LOGGER.warning(f"Fan speed control failed with endpoint {endpoint}: {response_json.get('msg', 'Unknown error')}")
                            continue
                            
                except Exception as e:
                    _LOGGER.warning(f"Fan speed control failed with endpoint {endpoint}: {e}")
                    continue
            
            raise Exception("All MarsPro fan speed control endpoints failed")

    def _generate_system_data(self):
        """Generate systemData payload for MarsPro with updated fields."""
        return json.dumps(
            {
                "reqId": int(time.time() * 1000),
                "appVersion": "2.0.0",  # Version MarsPro
                "osType": "android",
                "osVersion": "14",
                "deviceType": "SM-S928C",
                "deviceId": self.device_id,
                "netType": "wifi",
                "wifiName": "123",
                "timestamp": int(time.time()),
                "token": self.token,
                "timezone": "Europe/Berlin",
                "language": "French",  # Changé pour correspondre à vos préférences
                "appType": "marspro"  # Nouveau champ pour MarsPro
            }
        ) 