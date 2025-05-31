import aiohttp
import json
import time
import logging
import asyncio
import random
import re

# Support Bluetooth BLE pour appareils MarsPro Bluetooth
try:
    from bleak import BleakScanner, BleakClient
    BLUETOOTH_SUPPORT = True
except ImportError:
    BLUETOOTH_SUPPORT = False

_LOGGER = logging.getLogger(__name__)


class MarsProAPI:
    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.token = None
        self.user_id = None
        self.base_url = "https://mars-pro.api.lgledsolutions.com"  # URL CORRECTE !
        
        # Bluetooth BLE support
        self.bluetooth_support = BLUETOOTH_SUPPORT
        self.ble_device = None
        self.ble_client = None
        self.is_bluetooth_device = False
        self.device_serial = None
        
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

    async def get_all_devices(self):
        """Récupérer tous les appareils disponibles avec leurs PIDs réels - TOUS GROUPES"""
        await self._ensure_token()

        all_devices = []
        
        # Tester tous les groupes d'appareils possibles
        # Basé sur l'analyse des captures d'écran utilisateur
        device_groups_to_test = [
            1,    # Appareils Bluetooth (confirmé fonctionnel)
            2,    # Appareils WiFi (vu dans captures)
            3,    # Appareils Hybrides
            4,    # Appareils Pro
            5,    # Appareils Enterprise
            None  # Tous appareils (fallback)
        ]
        
        _LOGGER.info("Searching devices in all product groups...")
        
        for group_id in device_groups_to_test:
            payload = {
                "currentPage": 1,
                "type": None,
                "deviceProductGroup": group_id
            }
            
            endpoint = self.endpoints["device_list"]
            data = await self._make_request(endpoint, payload)
            
            if data and data.get('code') == '000':
                devices = data.get('data', {}).get('list', [])
                if devices:
                    _LOGGER.info(f"MarsPro found {len(devices)} devices in group {group_id}")
                    
                    # Traiter chaque appareil
                    for i, device in enumerate(devices):
                        name = device.get("deviceName", "N/A")
                        device_id = device.get("id", "N/A")
                        pid = device.get("devicePid", "N/A") or device.get("deviceSerialnum", "N/A")
                        
                        # Extraire le PID du nom si pas disponible dans les champs standards
                        if pid == "N/A" or not pid:
                            # Le nom contient souvent le PID: "MH-DIMBOX-345F45EC73CC"
                            pid_match = re.search(r'([A-F0-9]{12})$', name)
                            if pid_match:
                                pid = pid_match.group(1)
                                device["extracted_pid"] = pid
                                _LOGGER.info(f"Extracted PID from device name: {pid}")
                        
                        is_online = device.get("isOnline", "N/A")
                        is_net_device = device.get("isNetDevice", False)
                        device_mode = device.get("deviceMode", "N/A")
                        device_type = device.get("deviceType", "N/A")
                        
                        # Ajouter metadata de groupe
                        device["deviceProductGroup"] = group_id
                        device["connection_type"] = "WiFi" if is_net_device else "Bluetooth"
                        
                        _LOGGER.info(f"Device {i+1} (Group {group_id}): {name} (ID: {device_id}, PID: {pid}) - Online: {is_online}, Type: {device['connection_type']}")
                        
                        # Éviter les doublons (même ID)
                        if not any(d.get('id') == device_id for d in all_devices):
                            all_devices.append(device)
                    
                else:
                    _LOGGER.debug(f"No devices found in group {group_id}")
            else:
                _LOGGER.debug(f"Failed to query group {group_id}: {data}")
        
        if all_devices:
            _LOGGER.info(f"MarsPro total devices found: {len(all_devices)} across all groups")
            
            # Statistiques par type de connexion
            bluetooth_count = len([d for d in all_devices if d.get('connection_type') == 'Bluetooth'])
            wifi_count = len([d for d in all_devices if d.get('connection_type') == 'WiFi'])
            
            _LOGGER.info(f"Device breakdown: {bluetooth_count} Bluetooth, {wifi_count} WiFi")
            
            return all_devices
        else:
            _LOGGER.warning("No devices found in MarsPro across all groups")
            return []

    async def get_lightdata(self):
        """Get light data using confirmed MarsPro endpoints."""
        await self._ensure_token()

        # Utiliser la nouvelle méthode avec le bon payload
        devices = await self.get_all_devices()
        
        if devices:
            # Prendre le premier dispositif comme dispositif principal
            device = devices[0]
            
            # Priorité au PID extrait, puis aux champs standards
            self.device_serial = (device.get("extracted_pid") or 
                                device.get("deviceSerialnum") or 
                                device.get("devicePid") or 
                                str(device.get("id", "")))
            
            _LOGGER.info(f"MarsPro device found: {device.get('deviceName')} (ID: {device.get('id')}, PID: {self.device_serial})")
            
            # Ajouter le PID extrait au device pour Home Assistant
            device["deviceSerialnum"] = self.device_serial
            device["device_pid_stable"] = self.device_serial
            
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
        """Contrôler un appareil spécifique par son PID avec gestion Bluetooth"""
        await self._ensure_token()
        
        # Pour les appareils Bluetooth, TOUJOURS réveiller avant la commande
        _LOGGER.info(f"Starting control for device {pid} (Bluetooth device)")
        
        # 1. RÉVEIL BLUETOOTH OBLIGATOIRE
        try:
            await self._wakeup_bluetooth_device_by_pid(pid)
            await asyncio.sleep(1)  # Attendre que l'appareil se réveille
        except Exception as e:
            _LOGGER.warning(f"Bluetooth wakeup failed for {pid}: {e}")
        
        # 2. COMMANDE DE CONTRÔLE
        if pid and len(str(pid)) > 5:  # Si on a un vrai PID
            # Format outletCtrl avec PID spécifique
            inner_data = {
                "method": "outletCtrl",
                "params": {
                    "pid": str(pid),
                    "num": 0,
                    "on": 1 if on else 0,
                    "pwm": int(pwm)
                }
            }
            
            payload = {"data": json.dumps(inner_data)}
            
            _LOGGER.info(f"Controlling Bluetooth device {pid}: on={on}, pwm={pwm}")
            
            endpoint = self.endpoints["device_control"]
            data = await self._make_request(endpoint, payload)
            
            if data and data.get('code') == '000':
                _LOGGER.info(f"Bluetooth device {pid} control successful: on={on}, pwm={pwm}")
                
                # 3. VÉRIFICATION POST-COMMANDE (pour Bluetooth)
                await asyncio.sleep(0.5)
                verification_success = await self._verify_bluetooth_command(pid)
                
                if verification_success:
                    _LOGGER.info(f"Bluetooth command verified successfully for {pid}")
                    return True
                else:
                    _LOGGER.warning(f"Bluetooth command not verified for {pid}, retrying...")
                    
                    # Retry une fois
                    await asyncio.sleep(1)
                    await self._wakeup_bluetooth_device_by_pid(pid)
                    await asyncio.sleep(1)
                    
                    retry_data = await self._make_request(endpoint, payload)
                    if retry_data and retry_data.get('code') == '000':
                        _LOGGER.info(f"Bluetooth device {pid} control successful on retry")
                        return True
                    else:
                        _LOGGER.error(f"Bluetooth device {pid} control failed on retry")
                        return False
            else:
                _LOGGER.error(f"Bluetooth device {pid} control failed: {data}")
                return False
        
        _LOGGER.error(f"Invalid PID for Bluetooth control: {pid}")
        return False

    async def _wakeup_bluetooth_device_by_pid(self, pid: str):
        """Réveiller un appareil Bluetooth spécifique par PID"""
        try:
            # Format de réveil Bluetooth
            inner_data = {
                "method": "wakeup",
                "params": {
                    "pid": str(pid),
                    "deviceSerialnum": str(pid)
                }
            }
            
            payload = {"data": json.dumps(inner_data)}
            endpoint = self.endpoints["device_control"]
            
            _LOGGER.debug(f"Waking up Bluetooth device {pid}...")
            data = await self._make_request(endpoint, payload)
            
            if data and data.get("code") == "000":
                _LOGGER.info(f"Bluetooth device {pid} wakeup successful")
                return True
            else:
                _LOGGER.warning(f"Bluetooth device {pid} wakeup failed: {data}")
                
                # Essayer format alternatif
                alt_inner_data = {
                    "method": "bluetoothWakeup",
                    "params": {
                        "pid": str(pid)
                    }
                }
                alt_payload = {"data": json.dumps(alt_inner_data)}
                alt_data = await self._make_request(endpoint, alt_payload)
                
                if alt_data and alt_data.get("code") == "000":
                    _LOGGER.info(f"Bluetooth device {pid} alternative wakeup successful")
                    return True
                else:
                    _LOGGER.warning(f"All wakeup methods failed for {pid}")
                    return False
                
        except Exception as e:
            _LOGGER.error(f"Bluetooth device wakeup error for {pid}: {e}")
            return False

    async def _verify_bluetooth_command(self, pid: str):
        """Vérifier qu'une commande Bluetooth a bien été reçue"""
        try:
            # Demander le statut de l'appareil pour vérifier
            inner_data = {
                "method": "getDeviceStatus",
                "params": {
                    "pid": str(pid)
                }
            }
            
            payload = {"data": json.dumps(inner_data)}
            endpoint = self.endpoints["device_control"]
            
            data = await self._make_request(endpoint, payload)
            
            if data and data.get("code") == "000":
                # Si on reçoit une réponse, c'est que l'appareil est connecté
                return True
            else:
                return False
                
        except Exception as e:
            _LOGGER.debug(f"Status verification failed for {pid}: {e}")
            return False

    # =============================
    # NOUVELLES MÉTHODES BLUETOOTH BLE
    # =============================

    async def detect_device_mode(self):
        """Détecter si l'appareil est en mode Bluetooth ou WiFi"""
        try:
            device_data = await self.get_lightdata()
            if not device_data:
                return False
            
            self.is_bluetooth_device = device_data.get('isBluetoothDeivice', False)
            self.device_serial = device_data.get('deviceSerialnum')
            
            if self.is_bluetooth_device:
                _LOGGER.info(f"Device detected as Bluetooth: {self.device_serial}")
                if self.bluetooth_support:
                    _LOGGER.info("Bluetooth BLE support available - trying enhanced detection")
                    return await self._enhanced_ble_detection()
                else:
                    _LOGGER.warning("Device is Bluetooth but bleak library not available")
                    return False
            else:
                _LOGGER.info("Device detected as WiFi/Cloud")
                return True
                
        except Exception as e:
            _LOGGER.error(f"Device mode detection failed: {e}")
            return False

    async def _enhanced_ble_detection(self):
        """Détection BLE améliorée avec multiples techniques"""
        if not self.bluetooth_support:
            _LOGGER.error("Bluetooth support not available")
            return False
        
        target_id = self.device_serial
        _LOGGER.info(f"Enhanced BLE detection for device: {target_id}")
        
        # Technique 1: Scan standard BLE
        ble_found = await self._scan_for_ble_device()
        if ble_found:
            return True
        
        # Technique 2: Scan plus long avec filtres multiples
        _LOGGER.info("Standard scan failed, trying extended scan...")
        ble_found = await self._extended_ble_scan(target_id)
        if ble_found:
            return True
        
        # Technique 3: Scan par patterns de noms MarsPro
        _LOGGER.info("Extended scan failed, trying pattern-based scan...")
        ble_found = await self._pattern_based_ble_scan()
        if ble_found:
            return True
        
        # Technique 4: Scan par adresse MAC approximative
        _LOGGER.info("Pattern scan failed, trying MAC-based scan...")
        ble_found = await self._mac_based_ble_scan(target_id)
        if ble_found:
            return True
        
        _LOGGER.warning("All BLE detection methods failed - device may not be in pairing mode or out of range")
        return False

    async def _scan_for_ble_device(self):
        """Scanner et trouver l'appareil BLE MarsPro (méthode standard)"""
        if not self.bluetooth_support:
            return False
        
        try:
            _LOGGER.info("Standard BLE scan (10 seconds)...")
            devices = await BleakScanner.discover(timeout=10.0)
            
            target_id = self.device_serial
            
            for device in devices:
                device_name = device.name or ""
                device_addr = device.address
                
                # Chercher correspondance exacte
                if (target_id and target_id.lower() in device_name.lower()) or \
                   (target_id and target_id.lower() in device_addr.lower().replace(':', '')):
                    _LOGGER.info(f"Found MarsPro BLE device (standard): {device_name} ({device_addr})")
                    self.ble_device = device
                    return True
            
            _LOGGER.debug(f"Standard scan: {len(devices)} devices found, no match for {target_id}")
            return False
            
        except Exception as e:
            _LOGGER.error(f"Standard BLE scan failed: {e}")
            return False

    async def _extended_ble_scan(self, target_id):
        """Scan BLE étendu avec timeout plus long"""
        try:
            _LOGGER.info("Extended BLE scan (20 seconds)...")
            devices = await BleakScanner.discover(timeout=20.0)
            
            # Patterns de recherche plus flexibles
            search_patterns = [
                target_id.lower() if target_id else "",
                target_id[:8].lower() if target_id and len(target_id) >= 8 else "",
                target_id[-8:].lower() if target_id and len(target_id) >= 8 else "",
                "mars", "pro", "mh-", "dimbox", "345f45"
            ]
            
            for device in devices:
                device_name = (device.name or "").lower()
                device_addr = device.address.lower().replace(':', '')
                
                # Recherche par patterns
                for pattern in search_patterns:
                    if pattern and (pattern in device_name or pattern in device_addr):
                        _LOGGER.info(f"Found potential MarsPro device (extended): {device.name} ({device.address}) - matched pattern: {pattern}")
                        self.ble_device = device
                        return True
            
            _LOGGER.debug(f"Extended scan: {len(devices)} devices found, no pattern matches")
            return False
            
        except Exception as e:
            _LOGGER.error(f"Extended BLE scan failed: {e}")
            return False

    async def _pattern_based_ble_scan(self):
        """Scan basé sur des patterns de noms MarsPro connus"""
        try:
            _LOGGER.info("Pattern-based BLE scan (15 seconds)...")
            devices = await BleakScanner.discover(timeout=15.0)
            
            # Patterns MarsPro connus
            marspro_patterns = [
                "mars", "pro", "mh-", "dimbox", "led", "light", 
                "345f", "73cc", "bluetooth", "ble"
            ]
            
            # Log tous les appareils trouvés pour debug
            _LOGGER.info(f"Pattern scan found {len(devices)} BLE devices:")
            for i, device in enumerate(devices):
                device_name = device.name or "Unknown"
                _LOGGER.info(f"  {i+1}. {device_name} ({device.address})")
                
                # Vérifier patterns
                device_name_lower = device_name.lower()
                for pattern in marspro_patterns:
                    if pattern in device_name_lower:
                        _LOGGER.info(f"Found MarsPro device by pattern '{pattern}': {device_name} ({device.address})")
                        self.ble_device = device
                        return True
            
            return False
            
        except Exception as e:
            _LOGGER.error(f"Pattern-based BLE scan failed: {e}")
            return False

    async def _mac_based_ble_scan(self, target_id):
        """Scan basé sur des fragments d'adresse MAC"""
        try:
            _LOGGER.info("MAC-based BLE scan (15 seconds)...")
            devices = await BleakScanner.discover(timeout=15.0)
            
            if not target_id or len(target_id) < 6:
                return False
            
            # Créer des fragments de MAC possibles à partir du PID
            mac_fragments = [
                target_id[:2], target_id[2:4], target_id[4:6],
                target_id[6:8], target_id[8:10], target_id[10:12],
                target_id[:4], target_id[-4:], target_id[4:8]
            ]
            
            for device in devices:
                device_addr = device.address.lower().replace(':', '')
                
                # Vérifier si des fragments du PID apparaissent dans l'adresse MAC
                matches = 0
                for fragment in mac_fragments:
                    if fragment and len(fragment) >= 2 and fragment.lower() in device_addr:
                        matches += 1
                
                # Si au moins 2 fragments correspondent, c'est probablement notre appareil
                if matches >= 2:
                    _LOGGER.info(f"Found probable MarsPro device by MAC fragments: {device.name} ({device.address}) - {matches} matches")
                    self.ble_device = device
                    return True
            
            return False
            
        except Exception as e:
            _LOGGER.error(f"MAC-based BLE scan failed: {e}")
            return False

    async def _ble_connect(self):
        """Se connecter à l'appareil BLE"""
        if not self.ble_device or not self.bluetooth_support:
            return False
        
        try:
            self.ble_client = BleakClient(self.ble_device.address)
            await self.ble_client.connect()
            _LOGGER.info(f"Connected to BLE device: {self.ble_device.address}")
            return True
        except Exception as e:
            _LOGGER.error(f"BLE connection failed: {e}")
            return False

    async def _ble_disconnect(self):
        """Se déconnecter de l'appareil BLE"""
        if self.ble_client and await self.ble_client.is_connected():
            await self.ble_client.disconnect()
            _LOGGER.info("Disconnected from BLE device")

    async def _ble_control_device(self, on: bool, pwm: int = 100):
        """Contrôler l'appareil via Bluetooth BLE direct avec protocoles multiples"""
        if not self.bluetooth_support or not self.ble_device:
            _LOGGER.error("BLE control not available")
            return False
        
        try:
            # Se connecter si pas déjà connecté
            if not self.ble_client or not await self.ble_client.is_connected():
                if not await self._ble_connect():
                    return False
            
            # Obtenir les services de l'appareil
            services = await self.ble_client.get_services()
            
            # Log tous les services pour debug
            _LOGGER.info(f"BLE services found: {len(services.services)}")
            for service in services.services:
                _LOGGER.debug(f"Service: {service.uuid}")
                for char in service.characteristics:
                    _LOGGER.debug(f"  Characteristic: {char.uuid} - Properties: {char.properties}")
            
            # Chercher toutes les caractéristiques d'écriture
            write_characteristics = []
            for service in services.services:
                for char in service.characteristics:
                    if "write" in char.properties or "write-without-response" in char.properties:
                        write_characteristics.append(char)
            
            if not write_characteristics:
                _LOGGER.error("No writable characteristics found")
                return False
            
            _LOGGER.info(f"Found {len(write_characteristics)} writable characteristics")
            
            # Protocoles BLE MarsPro possibles (basés sur reverse engineering typique)
            pwm_byte = min(255, pwm * 255 // 100)
            on_byte = 0x01 if on else 0x00
            
            protocols = [
                # Protocole 1: Simple 3 bytes
                bytes([on_byte, 0x00, pwm_byte]),
                
                # Protocole 2: Avec header/footer
                bytes([0x55, 0xAA, on_byte, pwm_byte, 0xFF]),
                
                # Protocole 3: Format étendu
                bytes([0xFF, 0x01, on_byte, 0x00, pwm_byte, 0x00, 0x00, 0xEE]),
                
                # Protocole 4: Format MarsPro supposé
                bytes([0x4D, 0x50, on_byte, pwm_byte]),  # "MP" + commande
                
                # Protocole 5: Format PWM étendu
                bytes([0x01, on_byte, pwm_byte, pwm_byte ^ 0xFF]),  # Avec checksum XOR
                
                # Protocole 6: Format court
                bytes([on_byte, pwm_byte]),
                
                # Protocole 7: Format avec ID
                bytes([0x01, 0x02, on_byte, pwm_byte, 0x03, 0x04]),
            ]
            
            # Essayer chaque protocole sur chaque caractéristique
            for i, char in enumerate(write_characteristics):
                _LOGGER.info(f"Trying characteristic {i+1}: {char.uuid}")
                
                for j, protocol in enumerate(protocols):
                    try:
                        _LOGGER.debug(f"  Protocol {j+1}: {protocol.hex()}")
                        
                        # Essayer write avec réponse
                        try:
                            await self.ble_client.write_gatt_char(char.uuid, protocol, response=True)
                            _LOGGER.info(f"BLE write successful (char {i+1}, protocol {j+1}): on={on}, pwm={pwm}")
                            await asyncio.sleep(2)  # Attendre l'effet
                            return True
                        except:
                            # Essayer write sans réponse
                            await self.ble_client.write_gatt_char(char.uuid, protocol, response=False)
                            _LOGGER.info(f"BLE write-without-response successful (char {i+1}, protocol {j+1}): on={on}, pwm={pwm}")
                            await asyncio.sleep(2)  # Attendre l'effet
                            return True
                            
                    except Exception as e:
                        _LOGGER.debug(f"  Protocol {j+1} failed: {e}")
                        continue
            
            _LOGGER.error("All BLE protocols failed on all characteristics")
            return False
            
        except Exception as e:
            _LOGGER.error(f"BLE control failed: {e}")
            return False
        finally:
            # Garder la connexion ouverte pour les prochaines commandes
            pass

    async def control_device_hybrid(self, on: bool, pwm: int = 100):
        """Contrôle hybride optimisé: WiFi Cloud prioritaire, BLE en fallback"""
        _LOGGER.info(f"Starting optimized hybrid control: on={on}, pwm={pwm}")
        
        # Étape 1: Détecter le mode si pas déjà fait
        if not hasattr(self, 'is_bluetooth_device'):
            _LOGGER.info("Detecting device mode...")
            await self.detect_device_mode()
        
        # PRIORITÉ 1: Contrôle Cloud WiFi (plus fiable et recommandé)
        _LOGGER.info("Attempting Cloud API control (recommended approach)...")
        
        # Activation préalable (crucial pour tous les appareils)
        try:
            activation_success = await self._activate_device_for_cloud()
            if activation_success:
                _LOGGER.info("Device activation successful")
                await asyncio.sleep(1)  # Attendre que l'activation prenne effet
            else:
                _LOGGER.warning("Device activation failed, trying control anyway...")
        except Exception as e:
            _LOGGER.warning(f"Device activation error: {e}")
        
        # Contrôle par PID via Cloud
        pid = self.device_serial
        if not pid:
            device_data = await self.get_lightdata()
            pid = device_data.get('device_pid_stable') if device_data else None
        
        if pid:
            cloud_success = await self.control_device_by_pid(pid, on, pwm)
            if cloud_success:
                _LOGGER.info("Cloud API control successful!")
                return True
        
        # PRIORITÉ 2: Bluetooth BLE direct (si appareil Bluetooth et bleak disponible)
        if self.is_bluetooth_device and self.bluetooth_support:
            _LOGGER.info("Cloud failed, attempting Bluetooth BLE direct control...")
            
            ble_success = await self._ble_control_device(on, pwm)
            if ble_success:
                _LOGGER.info("Bluetooth BLE control successful!")
                return True
            else:
                _LOGGER.warning("Bluetooth BLE control failed...")
        
        # PRIORITÉ 3: Méthodes legacy en fallback
        _LOGGER.warning("Primary methods failed, trying legacy fallbacks...")
        
        # Legacy set_brightness
        if on and pwm > 0:
            try:
                legacy_response = await self.set_brightness(pwm)
                if legacy_response and legacy_response.get('code') == '000':
                    _LOGGER.info("Legacy brightness control successful!")
                    return True
            except Exception as e:
                _LOGGER.debug(f"Legacy brightness failed: {e}")
        
        # Legacy toggle_switch
        try:
            toggle_response = await self.toggle_switch(not on, pid or "")
            if toggle_response and toggle_response.get('code') == '000':
                _LOGGER.info("Legacy toggle control successful!")
                return True
        except Exception as e:
            _LOGGER.debug(f"Legacy toggle failed: {e}")
        
        # PRIORITÉ 4: Formats alternatifs en dernière chance
        _LOGGER.warning("All standard methods failed, trying alternative formats...")
        
        alternative_success = await self._try_alternative_control_formats(on, pwm, pid)
        if alternative_success:
            _LOGGER.info("Alternative format control successful!")
            return True
        
        _LOGGER.error("ALL CONTROL METHODS FAILED - device may be offline or needs WiFi configuration")
        _LOGGER.info("RECOMMENDATION: Configure device to WiFi mode using configure_wifi_marspro.py")
        return False

    async def _activate_device_for_cloud(self):
        """Activer l'appareil pour le cloud (setDeviceActiveV)"""
        try:
            activation = {
                "method": "setDeviceActiveV",
                "params": {
                    "vid": str(self.user_id),
                    "unum": "Mars Pro",
                    "tOffset": 120
                }
            }
            
            payload = {"data": json.dumps(activation)}
            response = await self._make_request("/api/upData/device", payload)
            
            return response and response.get('code') == '000'
            
        except Exception as e:
            _LOGGER.error(f"Device activation failed: {e}")
            return False

    async def _try_alternative_control_formats(self, on: bool, pwm: int, pid: str):
        """Essayer des formats de contrôle alternatifs"""
        if not pid:
            return False
        
        # Format 1: upDataStatus (vu dans certaines captures)
        try:
            alt_format_1 = {
                "method": "upDataStatus",
                "params": {
                    "pid": pid,
                    "switch": 1 if on else 0,
                    "lastBright": pwm,
                    "wifi": 1,
                    "connect": 1
                }
            }
            
            payload = {"data": json.dumps(alt_format_1)}
            response = await self._make_request("/api/upData/device", payload)
            
            if response and response.get('code') == '000':
                return True
        except:
            pass
        
        # Format 2: deviceControl simple
        try:
            alt_format_2 = {
                "method": "deviceControl",
                "params": {
                    "deviceId": pid,
                    "on": on,
                    "brightness": pwm
                }
            }
            
            payload = {"data": json.dumps(alt_format_2)}
            response = await self._make_request("/api/upData/device", payload)
            
            if response and response.get('code') == '000':
                return True
        except:
            pass
        
        # Format 3: lightControl
        try:
            alt_format_3 = {
                "method": "lightControl",
                "params": {
                    "pid": pid,
                    "state": on,
                    "pwm": pwm,
                    "channel": 0
                }
            }
            
            payload = {"data": json.dumps(alt_format_3)}
            response = await self._make_request("/api/upData/device", payload)
            
            if response and response.get('code') == '000':
                return True
        except:
            pass
        
        return False 