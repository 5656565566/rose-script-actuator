from selenium import webdriver
from selenium.webdriver import EdgeOptions, ChromeOptions, FirefoxOptions, EdgeService, ChromeService, FirefoxService
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By, ByType
from selenium.webdriver.remote.webdriver import WebDriver

from pathlib import Path
from typing import Union

from log import logger
from config import get_config, PATH_WORKING

import os

def switch_to_frame_with_element(driver: WebDriver, by: By, value: str) -> bool:
    """递归搜索元素并切换到包含该元素的 iframe。
    
    Args:
        driver (WebDriver): Selenium WebDriver 实例。
        by (By): 定位方法（如 By.XPATH, By.ID）。
        value (str): 定位方法对应的值。
        
    Returns:
        bool: 如果找到了元素并成功切换到对应的 iframe，返回 True，否则返回 False。
    """
    # 在当前上下文中查找元素
    try:
        driver.find_element(by, value)
        return True
    except Exception:
        pass
    
    # 获取所有 iframe 元素
    iframes = driver.find_elements(By.TAG_NAME, "iframe")
    
    # 递归遍历每个 iframe
    for i, iframe in enumerate(iframes):
        driver.switch_to.frame(iframe)
        if switch_to_frame_with_element(driver, by, value):
            return True
        # 切换回主内容，如果当前 iframe 不包含元素
        driver.switch_to.parent_frame()
    
    return False

class WebDevice:
    def __init__(self, name: str, driver_path: Path) -> None:
        self.name = name
        self.screenshot_file: bytes = b""
        self.pages: dict = {}
        self.driver_path = driver_path

        self.browser = None
        
    def _init_browser(self, driver_path: Path) -> WebDriver:
        """根据浏览器名称初始化浏览器实例。

        Args:
            driver_path: 浏览器驱动的路径。

        Returns:
            初始化的 WebDriver 实例。

        Raises:
            ValueError: 如果浏览器名称不支持或驱动路径无效。
        """
        if self.name == "Edge":
            options = EdgeOptions()
            service = EdgeService(executable_path=driver_path, log_output=os.devnull)
            logger.debug("使用 Edge 浏览器")
            self.browser = webdriver.Edge(service=service, options=options)
            self.actions = ActionChains(self.browser)
        elif self.name == "Chrome" and os.path.exists(driver_path):
            options = ChromeOptions()
            service = ChromeService(executable_path=driver_path, log_output=os.devnull)
            logger.debug("使用 Chrome 浏览器")
            self.browser = webdriver.Chrome(service=service, options=options)
            self.actions = ActionChains(self.browser)
        elif self.name == "Firefox" and os.path.exists(driver_path):
            options = FirefoxOptions()
            service = FirefoxService(executable_path=driver_path, log_output=os.devnull)
            logger.debug("使用 Firefox 浏览器")
            self.browser = webdriver.Firefox(service=service, options=options)
            self.actions = ActionChains(self.browser)
        else:
            raise ValueError(f"不支持的浏览器名称或无效的驱动路径: {self.name}")
    
    def _init_test(self):
        if not self.browser:
            return "请先打开一个页面 !"
    
    def open_url(self, url: str, name: str = None):
        
        if not name:
            name = url

        if len(self.pages) == 0:
            self._init_browser(self.driver_path)
            self.browser.get(url)
        
        
        
        self.pages[url] = url
    
    def close_url(self, name: str):
        # 如果是最后一个网页关闭浏览器
        pass
    
    def clickByText(self, text: str):
        """通过显示文本点击元素"""
        
        self._init_test()
        
        logger.debug(f"{self.page} 查找并点击显示文本为 '{text}' 的元素")
        
        if not switch_to_frame_with_element(self.browser, By.LINK_TEXT, text):
            return f"无法通过 {text} 找到元素"
        
        try:
            # 通过文本定位链接或按钮元素
            element = self.browser.find_element(By.LINK_TEXT, text)
            element.click()
            return f"点击成功: {text}"
        
        except Exception as e:
            return  f"无法通过文本 '{text}' 定位并点击元素: {e}"
    
    
    def clickByAny(self, by: ByType, any: str):
        """通过任意条件点击元素"""
        
        self._init_test()
        
        logger.debug(f"{self.page} 使用依据 {by} 查找并点击元素 {any}")
        
        if not switch_to_frame_with_element(self.browser, by, any):
            return f"无法通过 {any} 找到元素"
        
        try:
            element = self.browser.find_element(by, any)
            element.click()
            return f"点击成功: {any}"
        except Exception as e:
            return f"无法通过 '{any}' 定位并点击元素: {e}"
        
    
    def click(self, x: int, y: int):
        """在指定坐标点击"""
        
        self._init_test()
        
        y = y - 50
        
        self.actions.move_by_offset(x, y).click().perform()
        # 重置鼠标位置，以免后续操作受影响
        self.actions.move_by_offset(-x, -y).perform()
        return f"{self.page} 点击位置 {x}, {y}"
    
    def swipe(self, x1: int, y1: int, x2: int, y2: int, time: float) -> int:
        """模拟滑动"""
        
        self._init_test()
        
        y1 = y1 - 50
        y2 = y2 - 50
        
        self.actions.move_by_offset(x1, y1).click_and_hold().move_by_offset(x2 - x1, y2 - y1).release().perform()
        self.actions.move_by_offset(-x2, -y2).perform()
        
        return f"{self.page} 滑动 {x1}, {y1} => {x2}, {y2} 耗时 {time}"
    
    def textInput(self, text: Union[str, list]):
        """输入文本，支持中文及其他字符"""
        
        self._init_test()
        
        if isinstance(text, str):
            logger.debug(f"{self.page} 输入文本 {text}")
            self.actions.send_keys(text).perform()
        elif isinstance(text, list):
            for t in text:
                logger.debug(f"{self.page} 输入文本 {t}")
                self.actions.send_keys(t).perform()
        
        return f"{self.page} 输入文本 {text}"
    
    def shell(self, js: str):
        """执行 JS 脚本"""
        
        self._init_test()
        
        logger.debug(f"{self.page} 执行命令")
        result = self.browser.execute_script(js)
        return f"{self.page} 执行命令", result
    
    def screenshot(self, filePath: Path= None) -> Path:
        """保存屏幕截图"""
        save_object = None
        
        if get_config().save_screenshot:
            save_object = PATH_WORKING / "windows.png"
        
        if filePath:
            save_object = filePath
        
        try:
            self.screenshot_file = self.browser.get_screenshot_as_png()
            
            if save_object:
                with open(save_object, 'wb') as file:
                    file.write(self.screenshot_file)
                    return f"对 {self.browser.title} 的截图并保存到了 {save_object}", self.screenshot_file

                return f"对 {self.browser.title} 进行截图并保存到内存", self.screenshot_file
            
        except Exception as e:
            logger.warning(f"无法截图，请检查设备状态。错误信息: {e}")
            return f"无法截图，请检查设备状态。错误信息: {e}"

    def start_browser(self):
        self._init_browser()
    
    def kill_browser(self):
        """关闭浏览器"""
        self.browser.quit()  # 确保完全退出浏览器
