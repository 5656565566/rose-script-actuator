from base import Platform, register_platform

import platform

from .execute import WindowsDevice

@register_platform
class WindowsPlatform(Platform):
    def __init__(self) -> None:
        if platform.system() == "Windows":
            self.devices = [WindowsDevice()]
        
    @property
    def platform_name(self):
        return "Windows"
    
    @property
    def platform_decription(self):
        return "当运行在 Windows 设备上时可用"
    
    def get_all_device(self):
        return self.devices
    
    def select_deivce(self, name: str):
        return self.devices[0]