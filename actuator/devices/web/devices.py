from pathlib import Path

from base import Platform, register_platform
from config import get_config

from .execute import WebDevice

@register_platform
class WebDriverPlatform(Platform):
    """多网页管理"""
    def __init__(self):
        
        self.edge_driver = Path(get_config().web_drivers.get("msedgedriver", ""))
        self.chrome_driver = Path(get_config().web_drivers.get("chromedriver", ""))
        self.fire_fox = Path(get_config().web_drivers.get("geckodriver", ""))
            
    @property
    def platform_decription(self):
        return "通过前往配置文件配置 网页浏览器驱动路径 来添加 支持 msedgedriver(edge 浏览器), chromedriver(chrome 浏览器), geckodriver(firefox 浏览器)"
    
    @property
    def platform_name(self):
        return "网页浏览器"
    
    def get_all_device(self):
        
        self.devices = []
        
        if self.edge_driver.exists():
            self.devices.append(WebDevice("Edge", self.edge_driver))
            
        if self.chrome_driver.exists():
            self.devices.append(WebDevice("Chrome", self.edge_driver))
            
        if self.fire_fox.exists():
            self.devices.append(WebDevice("Firefox", self.edge_driver))
        
        return self.devices
    
    def select_deivce(self, name: str):
        
        for device in self.devices:
            if device.name == name:
                return device