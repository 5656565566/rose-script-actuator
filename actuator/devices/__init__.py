from typing import Type

from base import Platform, platforms

import _thread

class DevicesManager:
    def __init__(self):
        self.devices_list: list[Type[Platform]] = platforms
    
    def get_devices(self):
        
        devices = {}
        
        return devices
    
    def select(self, name: str):
        pass
    
    def execute(self, function: str, *args):
        for device in self.devices_list:
            if hasattr(device, function):
                _thread.start_new_thread(getattr(device, function), args)