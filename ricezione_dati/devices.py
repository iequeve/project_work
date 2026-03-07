import json
import os

class DeviceConfig:
    def __init__(self, device_id, ip, port, schema):
        self.id = device_id
        self.ip = ip
        self.port = port
        self.schema = schema

    def from_dict(data):
        return DeviceConfig(
            device_id=data['id'],
            ip=data['ip'],
            port=data['port'],
            schema=data.get('schema', []),
        )


def load_configs(config_path=None):
    if config_path is None:
        config_path = os.path.join(os.path.dirname(__file__), 'devices.json')
    with open(config_path, 'r') as file:
        raw_data = json.load(file)
    device_list = []
    for device_data in raw_data.get('devices', []):
        device_config = DeviceConfig.from_dict(device_data)
        device_list.append(device_config)
    return device_list