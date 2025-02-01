from tui import TuiApp
from config import read_conifg, get_config
from log import logger
from consts import threadings

from typing import Callable

import keyboard
import ctypes

notice_function: Callable = None
run_last_script_callback: Callable = None

def stop_script() -> None:
    notice_function("尝试停止所有脚本")
    logger.info("尝试停止所有脚本")
    
    for threading in threadings:
        thread_id = threading.ident
        ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, ctypes.py_object(SystemExit))
        
    notice_function(f"强行停止了运行中的 {len(threadings)} 个任务")
    logger.info(f"强行停止了运行中的 {len(threadings)} 个任务")
    threadings.clear()
    

def run_last_script() -> None:
    notice_function("尝试运行上一个脚本")

def main() -> None:
    app = TuiApp()
    
    global notice_function
    
    keyboard.add_hotkey(get_config().stop_key, stop_script)
    keyboard.add_hotkey(get_config().start_key, run_last_script)
    
    notice_function = app.notify
    
    app.run()

if __name__ == "__main__":
    read_conifg()
    main()
    exit()