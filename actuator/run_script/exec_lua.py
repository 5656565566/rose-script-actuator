from lupa import LuaError
from typing import Callable, Union
from pathlib import Path

import lupa
import time

from utils.requests import Requests

class VirtualFile:
    def __init__(self):
        self.content = []
        self.updata_buffer_handler = None
    
    def write(self, data):
        self.content.append(data)
        if self.updata_buffer_handler:
            self.updata_buffer_handler(data)
        return True

    def clear(self):
        self.content.clear()
    
    def read(self):
        return self.content
    
    def flush(self):
        pass

    def close(self):
        pass

class LuaExit(LuaError):
    ...

class LuaPath:
    def __init__(self, path: Union[str, Path]):
        
        self._path = path
        
        if isinstance(path, str):
            self._path = Path(path)
        
    def __str__(self):
        return str(self._path)
    
    def add(self, path: str):
        self._path = self._path / path
        return self._path

class LuaScriptRuntime:
    
    def output_handler(self, message: str = ""):
        """打印的映射"""
        self.buffer.write(f"{message}\n")
        
    def user_input_handler(self, prompt: str = "", description: str = ""):
        if self.user_input_callback is None:
            self.notify_handler("脚本使用了用户输入, 但当前运行环境不支持 !")
            return
        
        user_input = self.user_input_callback(prompt, description)
        return user_input
    
    def sleep_handler(self, seconds: float = 1.0):
        time.sleep(seconds)
    
    def stop_handler(self, message: str = ""):
        raise LuaExit(message)
    
    def notify_handler(self, message: str):
        if self.notify is None:
            return
        
        self.notify(message)

    def __init__(
        self,
        user_input_callback: Callable = None,
        notify: Callable = None,
    ):
        self.buffer = VirtualFile()
        self.user_input_callback = user_input_callback
        self.notify = notify
    
    def set_updata_buffer_handler(self, handler: Callable):
        self.buffer.updata_buffer_handler = handler
    
    def register_func(self):
        self.lua.globals()["Requests"] = Requests
    
    def init_lua(self):
        self.lua = lupa.LuaRuntime()

        self.buffer.clear()
        
        self.lua.globals()["print"] = self.output_handler
        self.lua.globals()["input"] = self.user_input_handler
        self.lua.globals()["notify"] = self.notify_handler if self.notify is not None else self.output_handler
        self.lua.globals()["clear_buffer"] = self.buffer.clear
        self.lua.globals()["work_path"] = LuaPath(Path.cwd())
        self.lua.globals()["path"] = LuaPath
        
        self.lua.globals()["exit"] = self.stop_handler
        
        self.lua.globals()["python_buffer_file"] = self.buffer
        self.lua.globals()["sleep"] = self.sleep_handler
        
        self.register_func()

        self.lua.execute("""
            local original_io_write = io.write
            local original_io_output = io.output
            local original_default_output = original_io_output()

            os.exit = exit
            
            function io.output(file)
                if file then
                    return original_io_output(file)
                else
                    return original_io_output()
                end
            end

            function io.write(...)
                local current_output = io.output()
                
                if current_output == original_default_output then
                    local data = table.concat({...})
                    python_buffer_file:write(data)
                    return true
                else
                    return original_io_write(...)
                end
            end
        """)
    
    def run(self, script: str):
        """调度 lua 脚本"""
        
        try:
            result = self.lua.execute(script)
        except LuaError as e:
            error_msg = str(e).split(':')[2:]
            error_msg = "".join(str(e).split(':')[2:])
            
            error_msg = (
                "你的脚本存在错误 !\n"
                f"错误信息：行数: {error_msg}\n"
            )
            self.output_handler(error_msg)
            return f"脚本语法错误 {e}"
        
        except LuaExit as e:
            return None
        
        except Exception as e:
            self.output_handler("本程序异常 !")
            self.output_handler(f"错误 {e}")
            return e
        
        else:
            if result not in [0, None]:
                self.output_handler(f"程序返回 {result}")
                return None