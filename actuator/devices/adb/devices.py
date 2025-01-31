from adbutils import AdbClient, adb, AdbTimeout

from log import logger
from config import get_config
from base import Platform, register_platform

import psutil

from .execute import Execute

def find_process_using_port(port: int) -> bool:
    """查询指定端口被哪个进程占用

    Args:
        port (int): 要查询的端口号。

    Returns:
        bool: 如果找到占用该端口的进程，返回包含进程信息的列表；否则，返回 None。
    """
    try:
        # 遍历所有网络连接
        connections = psutil.net_connections(kind= "inet")
        matching_connections = [conn for conn in connections if conn.laddr.port == port]
        
        if not matching_connections:
            return None
        
        process_info_list = []
        for conn in matching_connections:
            pid = conn.pid
            if pid is None:
                continue  # 有些连接可能没有关联的PID
            try:
                proc = psutil.Process(pid)
                process_info = {
                    "pid": pid,
                    "name": proc.name(),
                    "exe": proc.exe(),
                    "cmdline": proc.cmdline(),
                    "status": proc.status(),
                    "username": proc.username(),
                }
                process_info_list.append(process_info)
            except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                continue
        
        if process_info_list:
            return True
        else:
            return None

    except Exception as e:
        return None

@register_platform
class AdbPlatform(Platform):
    
    def __init__(self):
        try:
            self.adbclient = AdbClient()
            
        except Exception as e:
            logger.warning(f"platform adb loading failed. {e}")
            
        try:
            process = find_process_using_port(self.adbclient.port)
            
            if process:
                if "adb" not in process["exe"]:
                    logger.warning(f"port:{self.adbclient.port} maybe in used? change or add env:ANDROID_ADB_SERVER_PORT fix the warning.")
                    
        except:
            logger.debug(f"adbClient is running!")
        
        logger.debug(f"adbClient listening on port: {self.adbclient.port}")
        
        if wifi := get_config().extra.get("wifiadb", []):
            for wifi in wifi:
                try:
                    adb.connect(wifi, timeout=3.0)
                    logger.opt(colors=True).success(f"安卓设备 <y>{wifi}</y> <g>连接成功</g>")

                except AdbTimeout as e:
                    logger.opt(colors=True).error(f"安卓设备 <y>{wifi}</y> <r>连接失败</r> 设备未配对?")
        
        if len(self.adbclient.device_list()) > 1:
            logger.opt(colors=True).debug(f"Android 设备列表: ")

        for device in self.adbclient.device_list():
            
            self.executes[device.serial] = Execute(device)
            
            logger.opt(colors=True).debug(f"Android device: <g>{device.serial}</g>")
    
    def get_platform_decription(self):
        return
    
    def get_all_device(self):
        return
    
    def get_device_type():
        return
    
    def select_deivce(self, name: str):
        return