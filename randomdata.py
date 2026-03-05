import asyncio
import websockets
import json
import random
from datetime import datetime

from ricezione_dati.devices import load_configs, DeviceConfig


# simulatore vibecodato per test che manda dati randomici

class DeviceSimulator:
    # Simulatore di un singolo dispositivo basato sulla sua configurazione.

    def __init__(self, config: DeviceConfig):
        self.config = config

    def _generate_value(self, ftype: str):
        if ftype == "binary":
            return random.randint(0, 1)
        if ftype == "int":
            return random.randint(0, 100)
        return round(random.uniform(0, 100), 2)

    def _make_payload(self) -> dict:
        payload = {"device_id": self.config.id, "timestamp": datetime.now().isoformat()}
        for field in self.config.schema:
            name = field["name"]
            ftype = field.get("type", "float")
            payload[name] = self._generate_value(ftype)
        return payload

    async def run(self):
        uri = f"ws://{self.config.ip}:{self.config.port}"
        print(f"[CONNECTING] {self.config.id} → {uri}")
        try:
            async with websockets.connect(uri) as websocket:
                print(f"[CONNECTED] {self.config.id}")
                while True:
                    data = self._make_payload()
                    await websocket.send(json.dumps(data))
                    print(f"[SENT] {self.config.id}: {data}")
                    await asyncio.sleep(10)
        except ConnectionRefusedError:
            print(f"[ERROR] {self.config.id}: Impossibile connettersi a {uri}")
        except websockets.exceptions.ConnectionClosed:
            print(f"[DISCONNECTED] {self.config.id}: Connessione chiusa")
        except Exception as e:
            print(f"[ERROR] {self.config.id}: {e}")


async def main():
    configs = load_configs()
    sims = [DeviceSimulator(cfg) for cfg in configs]

    print(f"\nAvvio {len(sims)} simulatori di dispositivi...\n")

    try:
        await asyncio.gather(*(sim.run() for sim in sims))
    except KeyboardInterrupt:
        print("\n\nSimulazione interrotta.")


if __name__ == "__main__":
    asyncio.run(main())