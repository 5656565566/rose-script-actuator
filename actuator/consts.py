from threading import Thread
from devices import DevicesManager

threadings: list[Thread] = []
"""
存放脚本运行的线程
"""
devices_manager: DevicesManager = DevicesManager()
"""
设备管理器
"""