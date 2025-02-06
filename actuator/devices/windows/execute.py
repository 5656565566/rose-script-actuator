import pyautogui
import pygetwindow as gw
import pydirectinput
import pyperclip

from random import randint
from pathlib import Path
from io import BytesIO
from time import sleep, time
from typing import Optional, Union

from base import Devices
from config import get_config, PATH_WORKING
from log import logger
from model import Tip, Image

import psutil
import subprocess
import threading

LEFT = "left"
MIDDLE = "middle"
RIGHT = "right"
PRIMARY = "primary"
SECONDARY = "secondary"

mouseKey = Union[LEFT, MIDDLE, RIGHT, PRIMARY, SECONDARY]

class Application:
    def __init__(self, exe_path: Path, args: list[str] = []) -> None:
        self.exe_path = exe_path
        self.args = args
        self.process: Optional[subprocess.Popen] = None
        self.thread: Optional[threading.Thread] = None

    def start(self) -> None:
        if self.process and self.process.poll() is None:
            logger.debug("程序已在运行。")
            return

        def run():
            try:
                if self.args:
                    self.process = subprocess.Popen([self.exe_path] + self.args, cwd=self.exe_path.parent, shell=False)
                    
                else:
                    self.process = subprocess.Popen([self.exe_path], cwd=self.exe_path.parent, shell=False)
            
                logger.debug(f"启动程序: {self.exe_path} {' '.join(self.args)}")
                self.process.wait()
                logger.debug("程序已关闭。")
            except FileNotFoundError:
                logger.debug(f"未找到可执行文件: {self.exe_path}")
            except Exception as e:
                logger.debug(f"启动程序时发生错误: {e}")

        self.thread = threading.Thread(target=run, daemon=True)
        self.thread.start()

    def title(self, timeout: int = 10) -> Optional[str]:
        start_time = time()
        target_pid = self.process_id()
        
        while time() - start_time < timeout:
            windows = gw.getAllWindows()
            for window in windows:
                if window._pid == target_pid:
                    logger.debug(f"找到窗口: {window.title}")
                    return window.title
            sleep(0.5)
        
        logger.debug("未找到对应窗口。")
        return None


    def close(self) -> None:
        if not self.process:
            logger.debug("程序未启动。")
            return

        if self.process.poll() is not None:
            logger.debug("程序已关闭。")
            return

        try:
            # Attempt to close the window gracefully
            window_title = self.get_window_title()
            if window_title:
                window = gw.getWindowsWithTitle(window_title)[0]
                window.close()
                logger.debug(f"发送关闭命令到窗口: {window_title}")
                # Wait for the process to terminate
                self.process.wait(timeout=5)
                logger.debug("程序已关闭。")
            else:
                raise Exception("无法获取窗口标题，无法发送关闭命令。")
        except Exception as e:
            logger.debug(f"尝试关闭程序时发生错误: {e}")
            logger.debug("尝试强制终止程序。")
            self.force_close()

    def force_close(self) -> None:
        if not self.process:
            logger.debug("程序未启动。")
            return

        if self.process.poll() is None:
            try:
                # Use psutil to terminate the process tree
                proc = psutil.Process(self.process.pid)
                for child in proc.children(recursive=True):
                    child.terminate()
                proc.terminate()
                proc.wait(timeout=5)
                logger.debug("程序已被强制终止。")
            except Exception as e:
                logger.debug(f"强制终止程序时发生错误: {e}")
        else:
            logger.debug("程序已关闭。")

    def process_id(self) -> Optional[int]:
        if self.process and self.process.poll() is None:
            return self.process.pid
        return None

def contains_ascii(s: str) -> bool:
    return any(ord(char) < 128 for char in s)

class WindowsDevice(Devices):
    def __init__(self) -> None:
        self.name = "Windows"     
        self.applications: dict[str, Application] = {}
        self.random: bool = get_config().extra.get("random", True)
        self.screenshot_file = BytesIO()
    
    def openApp(self, name:str, exePath: Path, *args):
        
        if isinstance(exePath, str):
            exePath = Path(exePath)
        
        application = Application(exePath, args)
        
        self.applications[name] = application
        application.start()
        
        logger.debug(f"Windows 打开了 应用程序 {name}")
    
    def _offset(self, offset = None):
        """偏移"""
        return randint(-offset, offset)
    
    def gameClick(self, x: int, y: int, key: str = None) -> int:

        if key == None:
            key = PRIMARY

        x = x + (self._offset(5) if self.random else 0)
        y = y + (self._offset(5) if self.random else 0)
        
        pydirectinput.click(x, y, button=key)
        return Tip(f"Windows 点击位置 {x} {y}")
    
    def mouseClick(self, key: str) -> int:
        pyautogui.click(button=key)
        return Tip(f"点击鼠标按钮: {key}")
    
    def gameMouseClick(self, key: str) -> int:
        pydirectinput.click(button=key)
        return Tip(f"点击鼠标按钮: {key}")
    
    def getMouse(self) -> int:
        x, y = pyautogui.position()
        return Tip(f"当前鼠标位置: ({x}, {y})"), x, y
    
    def doubleClick(self, key: str = None) -> int:
        
        if key == None:
            key = PRIMARY
        
        x = x + (self._offset(5) if self.random else 0)
        y = y + (self._offset(5) if self.random else 0)

        pyautogui.doubleClick(x, y, button=key)
        return Tip(f"Windows 双击位置 {x} {y}")
    
    def gameDoubleClick(self, key: str = None) -> int:
        
        if key == None:
            key = PRIMARY
            
        x = x + (self._offset(5) if self.random else 0)
        y = y + (self._offset(5) if self.random else 0)

        pydirectinput.doubleClick(x, y, button=key)
        return Tip(f"Windows 双击位置 {x} {y}")
    
    def click(self, x: int, y: int, key: str = None) -> int:

        if key == None:
            key = PRIMARY
        
        x = x + (self._offset(5) if self.random else 0)
        y = y + (self._offset(5) if self.random else 0)
        
        pyautogui.click(x, y, button=key)
        return Tip(f"Windows 点击位置 {x} {y}")
    
    def textInput(self, text: Union[str, list]):
        
        if not contains_ascii(text):
            pyperclip.copy(text)
            pyautogui.hotkey('ctrl', 'v')
        
        else:
            pyautogui.typewrite(text)
        
        if isinstance(text, list):
            text = "".join(text)
        
        return Tip(f"windows 输入文本 {text}")
    
    def gameSwipe(self, x1: int, y1: int, x2: int, y2: int, time: float) -> int:
        if isinstance(x1, list):
            pass
        
        x1 = x1 + (self._offset(5) if self.random else 0)
        y1 = y1 + (self._offset(5) if self.random else 0)
        x2 = x2 + (self._offset(5) if self.random else 0)
        y2 = y2 + (self._offset(5) if self.random else 0)
        
        pydirectinput.moveTo(x1, y1, duration=time / 1000)
        pydirectinput.mouseDown(button="left")
        
        pydirectinput.moveTo(x2, y1, duration=time / 1000)
        pydirectinput.mouseUp(button="left")
        
        return Tip(f"Windows 鼠标滑动 {x1} {y1} => {x2} {y2} 耗时 {time}")
    
    def swipe(self, x1: int, y1: int, x2: int, y2: int, time: float) -> int:

        if isinstance(x1, list):
            pass
        
        x1 = x1 + (self._offset(5) if self.random else 0)
        y1 = y1 + (self._offset(5) if self.random else 0)
        x2 = x2 + (self._offset(5) if self.random else 0)
        y2 = y2 + (self._offset(5) if self.random else 0)
        
        pyautogui.moveTo(x1, y1, duration=time / 1000)
        pyautogui.mouseDown(button="left")
        
        pyautogui.moveTo(x2, y1, duration=time / 1000)
        pyautogui.mouseUp(button="left")
        
        return Tip(f"Windows 鼠标滑动 {x1} {y1} => {x2} {y2} 耗时 {time}")
    
    def gameKeyevent(self, key_id: str, time: int = 0) -> int:
        if time == 0:
            pydirectinput.press(key_id)
            return Tip(f"Windows 单击按键 {key_id}")
        
        else:
            pydirectinput.keyDown(key_id)
            sleep(time)
            pydirectinput.keyUp(key_id)
            return Tip(f"Windows 按住按键 {key_id} 耗时 {time}")
            
        
    
    def keyevent(self, key_id: str, time: int = 0) -> int:
        if time == 0:
            pyautogui.press(key_id)
            return Tip(f"Windows 单击按键 {key_id}")
        
        else:
            pyautogui.keyDown(key_id)
            sleep(time)
            pyautogui.keyUp(key_id)
            return Tip(f"Windows 按住按键 {key_id} 耗时 {time}")

    
    def hotkey(self, *hotkey):
        pyautogui.hotkey(hotkey)
        return Tip(f"Windows 按组合键 {hotkey}")
    
    def shell(self, cmd: str):
        try:
            result = subprocess.run(cmd, shell=True, check=True)
            return 0  # 成功返回 0
        except subprocess.CalledProcessError as e:
            return e.returncode  # 失败返回错误码
    
    def activateWindow(self, name: str):
        
        if not self.applications.get(name):
            return Tip(f"Windows 未找到窗口 {name}")
        
        application = self.applications.get(name)
        
        window = gw.getWindowsWithTitle(application.title())[0]
    
        window.activate()
        
        return Tip(f"Windows 切换到窗口 {name}")
    
    def get_all_windows_titles(self):
        return gw.getAllTitles()
    
    def get_screenshot(self) -> Image:
        return Image(self.screenshot_file.getvalue())
    
    def screenshot(self, filePath: Path= None):
        save_object = None
        
        self.screenshot_file.seek(0)
        self.screenshot_file.truncate(0)
        
        if get_config().save_screenshot:
            save_object = PATH_WORKING / "windows.png"
        
        if filePath:
            save_object = filePath
        
        try:
            screenshot = pyautogui.screenshot()
            screenshot.save(self.screenshot_file, format= "PNG")
            
            if save_object:
                screenshot.save(save_object, format=screenshot.format)
                return Tip(f"对 Windows 截图并保存到 {save_object}"), self.get_screenshot()
            
            return Tip(f"对 Windows 的截图并保存到了内存"), self.get_screenshot()
        
        except Exception as e:
            return Tip(f"无法为 Windows 设备 截图 请检查设备状态 {e}")