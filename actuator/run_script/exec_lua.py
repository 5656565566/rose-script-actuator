from lupa import LuaError
from typing import Callable, Union
from pathlib import Path

import lupa
import time
import inspect

from log import logger

from utils.requests import Requests
from utils.image import (
    crop_image,
    get_image_resolution,
    image_ocr,
    exact_match,
    simple_fuzzy_match,
    fuzzy_match,
    regex_match,
    template_matching,
    diff_size_template_matching
)

from consts import devices_manager

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

def dynamic_call(func, args):
    
    sig = inspect.signature(func)
    param_info = sig.parameters
    has_varargs = any(
        param.kind == inspect.Parameter.VAR_POSITIONAL for param in param_info.values()
    )

    if has_varargs:
        return func(*args)

    flat_args = []
    for arg in args:
        if isinstance(arg, (list, set)):
            flat_args.extend(arg)
        
        else:
            flat_args.append(arg)
    
    param_names = list(param_info.keys())
    required_params = [
        p for p in param_info.values() if p.default == inspect.Parameter.empty
    ]
    if len(flat_args) < len(required_params):
        raise Exception(
            f"参数不足，函数 {func.__name__} 需要至少 {len(required_params)} 个参数，实际传入 {len(flat_args)} 个参数"
        )

    bound_args = {}
    for i, param_name in enumerate(param_names):
        if i < len(flat_args):
            bound_args[param_name] = flat_args[i]
        elif param_info[param_name].default != inspect.Parameter.empty:
            bound_args[param_name] = param_info[param_name].default
        else:
            raise Exception(f"参数 {param_name} 未传入且无默认值")

    result = func(**bound_args)
    
    if isinstance(result, list):
        return tuple(result)
    
    return result

def output_result(output, callable: Callable):
    def wrapper(*args, **kwargs):
        result = dynamic_call(callable, args)
        if isinstance(result, tuple):
            output(result[0])
            return result[1:]
        else:
            output(result)
            
    return wrapper

class LuaDevice:
    def __init__(self, device, output):
        self.device = device
        self.output = output
    
    def update_device(self, device):
        self.device = device
    
    def __getitem__(self, name: str):
        
        if not self.device:
            raise LuaError("请先使用 select_device 选择设备 !")
        
        if not hasattr(self.device, name):
            raise LuaError(f"设备不存在 {name} 操作 !")
        
        return output_result(self.output, getattr(self.device, name))

class LuaImage:
    
    function_maps = {
        "crop_image": crop_image,
        "get_image_resolution": get_image_resolution,
        "ocr": image_ocr,
        "exact_match": exact_match,
        "simple_fuzzy_match": simple_fuzzy_match,
        "fuzzy_match": fuzzy_match,
        "regex_match": regex_match,
        "template_matching": template_matching,
        "diff_size_template_matching": diff_size_template_matching,
    }
    
    def __getitem__(self, name: str):
        
        if func := self.function_maps.get(name):
            return func
        
        raise LuaError(f"Image 不存在 {name} 操作 !")

class LuaScriptRuntime:
    
    def output_handler(self, message: str = ""):
        """打印的映射"""
        self.buffer.write(f"{message}\n")
    
    def print_handler(self, *args):
        self.output_handler(" ".join(map(str, args)))
    
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
    
    def select_device(self, name: str):
        devices_manager.init_platforms()
        devices_manager.select_devices(name)
        
        if devices_manager.device == None:
            self.notify(f"尝试切换设备 {name} 但它不存在", title="一个脚本执行错误", severity="error")
        
        self.lua.globals()["device"].update_device(devices_manager.device)
    
    def init_lua(self):
        self.lua = lupa.LuaRuntime()

        self.buffer.clear()
        
        self.lua.globals()["print"] = self.print_handler
        self.lua.globals()["input"] = self.user_input_handler
        self.lua.globals()["notify"] = self.notify_handler if self.notify is not None else self.output_handler
        self.lua.globals()["clear_buffer"] = self.buffer.clear
        self.lua.globals()["work_path"] = LuaPath(Path.cwd())
        self.lua.globals()["path"] = LuaPath
        
        self.lua.globals()["exit"] = self.stop_handler
        
        self.lua.globals()["python_buffer_file"] = self.buffer
        self.lua.globals()["sleep"] = self.sleep_handler
        
        self.lua.globals()["select_device"] = self.select_device
        self.lua.globals()["device"] = LuaDevice(None, self.output_handler)
        self.lua.globals()["image"] = LuaImage()
        
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
            #import traceback
            #logger.error(f"发生错误 {e.args[0]}")
            #error_message = "".join(traceback.format_exception(e))
            #logger.debug(error_message)
            
            self.output_handler("本程序异常 !")
            self.output_handler(f"错误 {e if str(e) else '未知错误'}")
            return e if str(e) else "未知错误"
        
        else:
            if result not in [0, None]:
                self.output_handler(f"程序返回 {result}")
                return None