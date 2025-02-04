from typing import Type

from base import Platform, platforms, Devices

class DevicesManager:
    def __init__(self):
        self.platforms_list: list[Type[Platform]] = []
        self.device: Type[Devices] = None
        
    def init_platforms(self):
        for platform in platforms:
            self.platforms_list.append(platform())
    
    def get_devices(self):
        devices: dict[str, list[Type[Devices]]] = {}
        
        for platform in self.platforms_list:
            platform.get_all_device()
        
        for platform in self.platforms_list:
            devices[f"{platform.platform_name}\n{platform.platform_decription}"] = platform.devices
        
        return devices
    
    def select_devices(self, name: str):
        for devices in self.get_devices().values():
            for device in devices:
                if device.name == name:
                    self.device = device
        
from .adb import AdbPlatform as AdbPlatform
from .windows import WindowsPlatform as WindowsPlatform
from .web import WebDriverPlatform as WebDriverPlatform