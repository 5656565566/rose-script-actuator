from adbutils import AdbDevice as _AdbDevice
from random import randint
from pathlib import Path
from typing import Union
from io import BytesIO

from base import Devices
from config import get_config, PATH_WORKING

class AdbDevice(Devices):
    def __init__(self, name: str, device: _AdbDevice) -> None:
        super().__init__(name)
        
        self.device = device
        self.random = get_config().extra.get("random", True)
        self.screenshot_file = BytesIO()
    
    def _offset(self, offset = None):
        """偏移"""
        return randint(-offset, offset)
    
    def click(self, x: int, y: int) -> int:

        x = x + (self._offset(5) if self.random else 0)
        y = y + (self._offset(5) if self.random else 0)

        self.device.click(x, y)

        return f"{self.device} 点击位置 {x} {y}"
    
    def swipe(self, x1: int, y1: int, x2: int, y2: int, time: float) -> int:

        x1 = x1 + (self._offset(5) if self.random else 0)
        y1 = y1 + (self._offset(5) if self.random else 0)
        x2 = x2 + (self._offset(5) if self.random else 0)
        y2 = y2 + (self._offset(5) if self.random else 0)
        self.device.swipe(x1, y1, x2, y2, time)

        return f"{self.device} 滑动 {x1} {y1} => {x2} {y2} 耗时 {time}"
    
    def keyevent(self, key_id: int) -> int:
        self.device.keyevent(key_id)
        return f"{self.device} 单击按键 {key_id}"
    
    def openApp(self, name: str, appActivity: str) -> int:

        self.device.shell(f'am start {appActivity}', timeout=2)

        return f"{self.device} 打开了 APP {name}"
    
    def textInput(self, text: Union[str, list]):
        
        if isinstance(text, list):
            text = "".join(text)
        
        self.device.shell(f'input text "{text}"', timeout=2)
        return f"{self.device} 输入文本 {text}"
    
    def shell(self, cmd: str):
        """终端执行命令"""
        
        return f"{self.device} 执行 命令 {cmd}", self.device.shell(cmd, timeout=2)
    
    
    def appName(self):
        """前台APP名"""
        
        res = self.device.shell("dumpsys activity activities | grep \"mResumedActivity\"", timeout=2)
        
        return f"{self.device} 前台 APP {res}", res
    
    def get_screenshot(self) -> bytes:
        return self.screenshot_file.getvalue()
    
    def screenshot(self, filePath: Path= None):
        
        save_object = self.screenshot_file
        
        if get_config().save_screenshot:
            save_object = PATH_WORKING / f"{self.name}.png"
            
        if filePath:
            save_object = filePath
        
        try:
            self.device.screenshot().save(save_object)
            
            if isinstance(save_object, BytesIO):
                return f"对 {self.device} 进行截图并保存到内存", save_object.getvalue()
            
        except:
            return f"无法为 {self.device.serial} 截图 请检查设备状态", False
        else:
            return f"{self.device} 截图并保存到了 {save_object}"