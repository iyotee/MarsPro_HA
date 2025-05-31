#!/usr/bin/env python3
"""
🔵 TEST APPAREIL BLUETOOTH - MZL001
Teste des commandes spécifiques pour appareils Bluetooth
"""

import asyncio
import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'custom_components', 'marshydro'))

from api_marspro import MarsProAPI

class BluetoothMarsProTester(MarsProAPI):
    """Testeur spécialisé pour appareils Bluetooth"""
    
    async def test_start_device(self):
        """Tenter de démarrer l'appareil (isStart: 0 → 1)"""
        await self._ensure_token()
        
        # Test 1: Commande de démarrage simple
        payload = {
            "deviceId": self.device_id,
            "command": "start"
        }
        
        endpoint = "/api/upData/device"
        
        print(f"🚀 Test START device...")
        print(f"📝 Payload: {json.dumps(payload, indent=2)}")
        
        data = await self._make_request(endpoint, payload)
        print(f"📤 Réponse: {json.dumps(data, indent=2) if data else 'None'}")
        return data
        
    async def test_bluetooth_control(self, brightness):
        """Test contrôle spécifique Bluetooth"""
        await self._ensure_token()
        
        # Format pour Bluetooth avec deviceSerialnum
        inner_data = {
            "method": "bluetoothCtrl",  # Méthode spécifique BT
            "params": {
                "deviceSerialnum": self.device_serial,
                "brightness": int(brightness),
                "isOn": True
            }
        }
        
        payload = {
            "data": json.dumps(inner_data)
        }
        
        endpoint = "/api/upData/device"
        
        print(f"🔵 Test contrôle Bluetooth...")
        print(f"📝 Payload: {json.dumps(payload, indent=2)}")
        
        data = await self._make_request(endpoint, payload)
        print(f"📤 Réponse: {json.dumps(data, indent=2) if data else 'None'}")
        return data
        
    async def test_device_wakeup(self):
        """Tenter de réveiller l'appareil"""
        await self._ensure_token()
        
        inner_data = {
            "method": "wakeup",
            "params": {
                "deviceSerialnum": self.device_serial
            }
        }
        
        payload = {
            "data": json.dumps(inner_data)
        }
        
        endpoint = "/api/upData/device"
        
        print(f"⏰ Test WAKEUP device...")
        print(f"📝 Payload: {json.dumps(payload, indent=2)}")
        
        data = await self._make_request(endpoint, payload)
        print(f"📤 Réponse: {json.dumps(data, indent=2) if data else 'None'}")
        return data
        
    async def test_bluetooth_switch(self, is_on):
        """Test switch Bluetooth"""
        await self._ensure_token()
        
        inner_data = {
            "method": "bluetoothSwitch",
            "params": {
                "deviceSerialnum": self.device_serial,
                "isOn": is_on
            }
        }
        
        payload = {
            "data": json.dumps(inner_data)
        }
        
        endpoint = "/api/upData/device"
        
        print(f"🔵 Test {'ON' if is_on else 'OFF'} Bluetooth...")
        print(f"📝 Payload: {json.dumps(payload, indent=2)}")
        
        data = await self._make_request(endpoint, payload)
        print(f"📤 Réponse: {json.dumps(data, indent=2) if data else 'None'}")
        return data

async def main():
    print("🔵 TEST APPAREIL BLUETOOTH MZL001")
    print("=" * 50)
    
    email = "jeremy.noverraz2@proton.me"
    password = "T00rT00r"
    
    try:
        tester = BluetoothMarsProTester(email, password)
        
        # Connexion
        await tester.login()
        print("✅ Connexion réussie\n")
        
        # Récupérer l'appareil
        light_data = await tester.get_lightdata()
        if not light_data:
            print("❌ Aucun appareil trouvé")
            return
            
        print(f"📱 Appareil: {light_data['deviceName']}")
        print(f"🔵 Type: Bluetooth Device (MZL001)")
        print(f"🆔 Device ID: {light_data['id']}")
        print(f"🔢 Serial: {light_data['deviceSerialnum']}")
        print()
        
        # Test 1: Essayer de démarrer l'appareil
        print("🧪 TEST 1: Démarrer l'appareil")
        print("-" * 30)
        await tester.test_start_device()
        await asyncio.sleep(2)
        print()
        
        # Test 2: Wakeup
        print("🧪 TEST 2: Réveiller l'appareil")
        print("-" * 30)
        await tester.test_device_wakeup()
        await asyncio.sleep(2)
        print()
        
        # Test 3: Switch Bluetooth ON
        print("🧪 TEST 3: Switch Bluetooth ON")
        print("-" * 30)
        await tester.test_bluetooth_switch(True)
        await asyncio.sleep(2)
        print()
        
        # Test 4: Contrôle Bluetooth
        print("🧪 TEST 4: Contrôle Bluetooth 75%")
        print("-" * 30)
        await tester.test_bluetooth_control(75)
        await asyncio.sleep(2)
        print()
        
        # Test 5: Essayer le format outletCtrl normal mais avec force
        print("🧪 TEST 5: outletCtrl forcé")
        print("-" * 30)
        inner_data = {
            "method": "outletCtrl",
            "params": {
                "pid": tester.device_serial,
                "num": 0,
                "on": 1,
                "pwm": 90,
                "force": True  # Forcer la commande
            }
        }
        
        payload = {"data": json.dumps(inner_data)}
        data = await tester._make_request("/api/upData/device", payload)
        print(f"📤 Réponse: {json.dumps(data, indent=2) if data else 'None'}")
        print()
        
        print("👀 REGARDEZ VOTRE LAMPE - A-t-elle réagi ?")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 