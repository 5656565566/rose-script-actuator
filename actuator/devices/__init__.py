from typing import Type

from base import Platform, platforms

from .adb import AdbPlatform as AdbPlatform

class DevicesManager:
    def __init__(self):
        self.platforms_list: list[Type[Platform]] = []
        
    def init_platforms(self):
        for platform in platforms:
            self.platforms_list.append(platform())
    
    def get_devices(self):
        devices = {}
        return devices
    
    def select(self, name: str):
        pass
    
    def __call__(self, function: str, *args):
        pass