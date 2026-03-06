import json
import os

class DeviceConfig:
    # carica json dei dispositivi e restituisce info
    def __init__(self, device_id: str, ip: str, port: int, schema: list):
        self.id = device_id
        self.ip = ip
        self.port = port
        self.schema = schema

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            device_id=data['id'],
            ip=data['ip'],
            port=data['port'],
            schema=data.get('schema', []),
        )


def load_configs(config_path=None):
    if config_path is None:
        config_path = os.path.join(os.path.dirname(__file__), 'devices.json')
    with open(config_path, 'r') as f:
        raw = json.load(f)
    return [DeviceConfig.from_dict(d) for d in raw.get('devices', [])]