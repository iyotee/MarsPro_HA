import aiohttp
import json
import time
import logging
import asyncio
import random

_LOGGER = logging.getLogger(__name__)


class MarsProAPI:
    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.token = None
        self.user_id = None
        self.base_url = "https://mars-pro.api.lgledsolutions.com"  # URL CORRECTE !
        
        # Endpoints découverts et confirmés fonctionnels
        self.endpoints = {
            "login": "/api/android/ulogin/mailLogin/v1",  # ENDPOINT QUI MARCHE !
            "device_list": "/api/android/udm/getDeviceList/v1",  # ENDPOINT CONFIRMÉ !
            "device_detail": "/api/android/udm/getDeviceDetail/v1",  # ENDPOINT CONFIRMÉ !
            "mine_info": "/api/android/mine/info/v1",  # ENDPOINT CONFIRMÉ !
            "device_control": "/api/upData/device"  # ENDPOINT RÉEL CAPTURÉ !
        }
        self.api_lock = asyncio.Lock()
        self.last_login_time = 0
        self.login_interval = 300  # Minimum interval between logins in seconds
        self.device_id = None

    async def _make_request(self, endpoint, payload):
        """Faire une requête avec les vrais paramètres capturés"""
        url = f"{self.base_url}{endpoint}"
        
        # Headers exacts capturés de l'app MarsPro RÉELLE !
        systemdata = {
            "reqId": str(random.randint(10000000000, 99999999999)),
            "appVersion": "1.3.2",  # Version exacte de l'app
            "osType": "android",
            "osVersion": "15",      # Version exacte capturée
            "deviceType": "SM-S928B",  # Type exact capturé
            "deviceId": "AP3A.240905.015.A2",  # ID exact capturé
            "netType": "wifi",
            "wifiName": "unknown",  # Valeur exacte capturée
            "timestamp": str(int(time.time())),
            "timezone": "34",       # Timezone exacte capturée
            "language": "French"
        }
        
        # Ajouter le token si disponible
        if self.token:
            systemdata["token"] = self.token
        
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Dart/3.4 (dart:io)',  # User-Agent exact capturé
            'systemdata': json.dumps(systemdata)
        }
        
        _LOGGER.debug(f"MarsPro request to {url}")
        _LOGGER.debug(f"Headers: {headers}")
        _LOGGER.debug(f"Payload: {payload}")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=headers, timeout=30) as response:
                    if response.status == 200:
                        data = await response.json()
                        _LOGGER.debug(f"MarsPro response: {data}")
                        return data
                    else:
                        _LOGGER.error(f"MarsPro HTTP error: {response.status}")
                        return None
                        
        except Exception as e:
            _LOGGER.error(f"MarsPro request failed: {e}")
            return None

    async def login(self):
        """Connexion avec les vrais paramètres découverts"""
        # Payload exact basé sur l'analyse réseau
        payload = {
            "email": self.email,
            "password": self.password, 
            "loginMethod": "1"  # Méthode email/password
        }
        
        # Utiliser l'endpoint de login confirmé fonctionnel
        endpoint = self.endpoints["login"]
        data = await self._make_request(endpoint, payload)
        
        if data and data.get('code') == '000':  # Code de succès MarsPro
            self.token = data['data']['token']
            self.user_id = data['data']['userId']
            _LOGGER.info("MarsPro authentication successful!")
            return True
        else:
            error_msg = data.get('msg', 'Unknown error') if data else "No response"
            _LOGGER.error(f"MarsPro authentication failed: {error_msg}")
            raise Exception(f"MarsPro authentication failed: {error_msg}")

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
            self.legacy_api = legacy_module.MarsHydroAPI(self.email, self.password)
            await self.legacy_api.login()
            
            # Copier les données importantes
            self.token = self.legacy_api.token
            self.legacy_base_url = self.legacy_api.base_url
            
            _LOGGER.info("Fallback to legacy API successful")
            
        except Exception as e:
            _LOGGER.error(f"Fallback to legacy API failed: {e}")
            raise Exception(f"Both MarsPro and legacy MarsHydro APIs failed. MarsPro: No valid credentials, Legacy: {e}")

    async def _fallback_get_lightdata(self):
        """Récupérer les données d'éclairage via l'API legacy"""
        if hasattr(self, 'legacy_api'):
            return await self.legacy_api.get_lightdata()
        else:
            raise Exception("Legacy API not initialized")

    async def _fallback_get_fandata(self):
        """Récupérer les données de ventilateur via l'API legacy"""
        if hasattr(self, 'legacy_api'):
            return await self.legacy_api.get_fandata()
        else:
            raise Exception("Legacy API not initialized")

    async def safe_api_call(self, func, *args, **kwargs):
        """Ensure thread-safe API calls."""
        async with self.api_lock:
            return await func(*args, **kwargs)

    async def _ensure_token(self):
        """Ensure that the token is valid."""
        if not self.token:
            await self.login()

    async def toggle_switch(self, is_close: bool, device_id: str):
        """Toggle the light or fan switch (on/off) - MarsPro version avec format EXACT des captures."""
        await self._ensure_token()

        # Si pas de device_serial, récupérer les données du dispositif
        if not hasattr(self, 'device_serial') or not self.device_serial:
            device_data = await self.get_lightdata()
            if not device_data:
                _LOGGER.error("Cannot toggle switch: no device data available")
                return

        # Utiliser le PID fourni ou celui récupéré automatiquement
        target_pid = device_id if device_id else self.device_serial
        
        if not target_pid:
            _LOGGER.error("No device PID available for control")
            return

        # Utiliser la nouvelle méthode de contrôle par PID
        success = await self.control_device_by_pid(target_pid, not is_close, 100)
        
        if success:
            _LOGGER.info(f"MarsPro switch toggle successful (PID: {target_pid})")
            return {"code": "000", "msg": "success"}
        else:
            _LOGGER.warning("MarsPro control failed, trying fallback...")
            return await self._legacy_toggle_switch(is_close, device_id)

    async def _legacy_toggle_switch(self, is_close: bool, device_id: str):
        """Méthode de contrôle legacy en fallback avec format outletCtrl"""
        # Format legacy conservé comme fallback
        inner_data = {
            "method": "outletCtrl",
            "params": {
                "pid": self.device_serial,
                "num": 0,
                "on": 0 if is_close else 1,
                "pwm": 100
            }
        }
        
        payload = {"data": json.dumps(inner_data)}
        endpoint = "/api/upData/device"  # Endpoint legacy
        
        return await self._make_request(endpoint, payload)

    async def _process_device_list(self, device_product_group):
        """Retrieve device list for a given product group - MarsPro version."""
        await self._ensure_token()
        
        # Payload exact capturé !
        payload = {
            "currentPage": 1,
            "type": None,
            "deviceProductGroup": device_product_group
        }

        # ENDPOINT EXACT QUI MARCHE !
        endpoint = "/api/android/udm/getDeviceList/v1"
        
        data = await self._make_request(endpoint, payload)
        
        if data and data.get("code") == "000":
            device_list = data.get("data", {}).get("list", [])
            _LOGGER.info(f"MarsPro found {len(device_list)} devices")
            return device_list
        else:
            error_msg = data.get('msg', 'Unknown error') if data else "No response"
            _LOGGER.error(f"Device list failed: {error_msg}")
            return []

    async def get_lightdata(self):
        """Get light data using confirmed MarsPro endpoints."""
        await self._ensure_token()

        # Utiliser l'endpoint de liste des dispositifs confirmé
        payload = {
            "pageNum": 1,
            "pageSize": 50  # Récupérer tous les dispositifs
        }
        
        endpoint = self.endpoints["device_list"]
        data = await self._make_request(endpoint, payload)
        
        if data and data.get('code') == '000':
            devices = data.get('data', {}).get('list', [])
            if devices:
                # Prendre le premier dispositif comme dispositif principal
                device = devices[0]
                self.device_serial = device.get("deviceSerialnum")
                _LOGGER.info(f"MarsPro device found: {device.get('deviceName')} (PID: {self.device_serial})")
                return device
        
        _LOGGER.warning("No devices found in MarsPro, trying fallback...")
        # Fallback vers l'API legacy si aucun dispositif trouvé
        try:
            await self._fallback_to_legacy_api()
            return await self._fallback_get_lightdata()
        except Exception as e:
            _LOGGER.error(f"Both MarsPro and fallback failed: {e}")
            return None

    async def get_fandata(self):
        """Get fan data using confirmed MarsPro endpoints."""
        # Pour l'instant, utilise les mêmes données que les lumières
        # car les ventilateurs sont souvent intégrés aux dispositifs d'éclairage
        return await self.get_lightdata()

    async def set_brightness(self, brightness):
        """Set the brightness of the MarsPro light avec format outletCtrl simple des captures."""
        await self._ensure_token()

        # Si pas de device_serial, récupérer les données du dispositif
        if not hasattr(self, 'device_serial') or not self.device_serial:
            device_data = await self.get_lightdata()
            if not device_data:
                _LOGGER.error("Cannot set brightness: no device data available")
                return

        # Utiliser la nouvelle méthode de contrôle par PID
        success = await self.control_device_by_pid(self.device_serial, True, brightness)
        
        if success:
            _LOGGER.info(f"MarsPro brightness set to {brightness}% (PID: {self.device_serial})")
            return {"code": "000", "msg": "success"}
        else:
            error_msg = f"Brightness control failed for PID: {self.device_serial}"
            _LOGGER.error(error_msg)
            raise Exception(error_msg)

    async def _wakeup_bluetooth_device(self):
        """Réveiller un appareil Bluetooth avant de l'utiliser"""
        try:
            inner_data = {
                "method": "wakeup",
                "params": {
                    "deviceSerialnum": self.device_serial
                }
            }
            
            payload = {"data": json.dumps(inner_data)}
            endpoint = "/api/upData/device"
            
            _LOGGER.debug("Waking up Bluetooth device...")
            data = await self._make_request(endpoint, payload)
            
            if data and data.get("code") == "000":
                _LOGGER.info("Bluetooth device wakeup successful")
                # Petit délai pour laisser l'appareil se réveiller
                await asyncio.sleep(1)
            else:
                _LOGGER.warning(f"Bluetooth device wakeup failed: {data}")
                
        except Exception as e:
            _LOGGER.warning(f"Bluetooth device wakeup error: {e}")

    async def set_fanspeed(self, speed, fan_device_id):
        """Set the speed of the MarsPro fan avec format outletCtrl simple des captures."""
        await self._ensure_token()

        # Format EXACT de la capture 3 : outletCtrl simple pour ventilateur
        inner_data = {
            "method": "outletCtrl",  # Format SIMPLE capturé !
            "params": {
                "pid": self.device_serial or fan_device_id,  # PID comme dans capture 3
                "num": 0,                   # num: 0 comme dans capture 3  
                "on": 1,                    # on: 1 pour allumer le ventilateur
                "pwm": int(speed)           # pwm: vitesse comme luminosité
            }
        }

        payload = {"data": json.dumps(inner_data)}

        _LOGGER.debug(f"MarsPro fan speed payload (outletCtrl format): {json.dumps(payload, indent=2)}")

        endpoint = "/api/upData/device"  # Endpoint réel capturé
        
        data = await self._make_request(endpoint, payload)
        
        if data and data.get("code") == "000":
            _LOGGER.info(f"MarsPro fan speed set to {speed}% successfully (outletCtrl format)")
            return data
        else:
            error_msg = data.get('msg', 'Unknown error') if data else "No response"
            _LOGGER.error(f"MarsPro fan speed control failed: {error_msg}")
            raise Exception(f"MarsPro fan speed control failed: {error_msg}")

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

    async def get_all_devices(self):
        """Récupérer tous les appareils disponibles avec leurs PIDs réels"""
        await self._ensure_token()

        payload = {
            "pageNum": 1,
            "pageSize": 50
        }
        
        endpoint = self.endpoints["device_list"]
        data = await self._make_request(endpoint, payload)
        
        if data and data.get('code') == '000':
            devices = data.get('data', {}).get('list', [])
            _LOGGER.info(f"MarsPro found {len(devices)} total devices")
            
            # Log des informations détaillées sur chaque appareil
            for i, device in enumerate(devices):
                name = device.get("deviceName", "N/A")
                pid = device.get("deviceSerialnum", "N/A")
                status = "ON" if not device.get("isClose", False) else "OFF"
                device_type = device.get("productType", "N/A")
                _LOGGER.info(f"Device {i+1}: {name} (PID: {pid}) - {status} - Type: {device_type}")
            
            return devices
        else:
            _LOGGER.warning("No devices found in MarsPro")
            return []

    async def get_device_by_name(self, device_name: str):
        """Récupérer un appareil spécifique par son nom"""
        devices = await self.get_all_devices()
        
        for device in devices:
            if device.get("deviceName", "").lower() == device_name.lower():
                self.device_serial = device.get("deviceSerialnum")
                _LOGGER.info(f"Found device '{device_name}' with PID: {self.device_serial}")
                return device
        
        _LOGGER.warning(f"Device '{device_name}' not found")
        return None

    async def control_device_by_pid(self, pid: str, on: bool, pwm: int = 100):
        """Contrôler un appareil spécifique par son PID"""
        await self._ensure_token()
        
        # Format outletCtrl avec PID spécifique
        inner_data = {
            "method": "outletCtrl",
            "params": {
                "pid": pid,
                "num": 0,
                "on": 1 if on else 0,
                "pwm": int(pwm)
            }
        }
        
        payload = {"data": json.dumps(inner_data)}
        
        _LOGGER.debug(f"Controlling device {pid}: on={on}, pwm={pwm}")
        
        endpoint = self.endpoints["device_control"]
        data = await self._make_request(endpoint, payload)
        
        if data and data.get('code') == '000':
            _LOGGER.info(f"Device {pid} control successful: on={on}, pwm={pwm}")
            return True
        else:
            error_msg = data.get('msg', 'Unknown error') if data else "No response"
            _LOGGER.error(f"Device {pid} control failed: {error_msg}")
            return False 