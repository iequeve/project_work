import asyncio
import websockets
import json

from .devices import load_configs, DeviceConfig


class DeviceServer:

    def __init__(self, config: DeviceConfig):
        self.config = config

    async def handle(self, websocket):
        print("\n\n\n")
        print(f"{self.config.id} connesso su ip {self.config.ip} porta {self.config.port})")
        print("\n")

        try:
            async for message in websocket:
                data = json.loads(message)
                self.process_payload(data)
                await websocket.send(json.dumps({"status": "ok"}))
        except websockets.exceptions.ConnectionClosed:
            print(f"\n{self.config.id} disconnesso su ip {self.config.ip} porta {self.config.port}")

    def process_payload(self, data: dict):
        ts = data.get("timestamp", "N/A")
        print(f"\n[{self.config.id}] {ts}")
        for field in self.config.schema:
            name = field.get("name")
            value = data.get(name)
            print(f"\n{name}: {value}")

    async def run(self):
        async with websockets.serve(self.handle, self.config.ip, self.config.port):
            print(f"\nServer in ascolto su {self.config.ip}:{self.config.port} per {self.config.id}")
            await asyncio.Future()




# prende i dispositivi da devices.py e avvia un server per ognuno
async def start_all_servers():
    configs = load_configs()
    servers = [DeviceServer(cfg) for cfg in configs]

    print("\n\n\n")
    print(f"Avvio {len(servers)} server\n")

    await asyncio.gather(*(srv.run() for srv in servers))