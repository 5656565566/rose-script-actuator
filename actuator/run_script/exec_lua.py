from pathlib import Path
from typing import Callable, Union, Any
import time

from lupa.lua54 import LuaRuntime, LuaError
from log import logger

from model import Tip, Image
from utils.requests import Requests
from utils.image import (
    image_ocr,
    exact_match,
    simple_fuzzy_match,
    fuzzy_match,
    regex_match,
    template_matching,
    diff_size_template_matching,
)
from utils.method import dynamic_call
from consts import devices_manager


class VirtualFile:
    """模拟文件对象用于缓冲输出"""
    
    def __init__(self):
        self.content = []
        self.updata_buffer_handler: Callable | None = None

    def write(self, data: str) -> bool:
        """写入数据并触发更新回调"""
        self.content.append(data)
        if self.updata_buffer_handler:
            self.updata_buffer_handler(data)
        return True

    def clear(self) -> None:
        """清空缓冲区"""
        self.content.clear()

    def read(self) -> list[str]:
        """读取缓冲区内容"""
        return self.content

    def flush(self) -> None:
        """保持文件接口兼容性"""
        pass

    def close(self) -> None:
        """保持文件接口兼容性"""
        pass


class LuaExit(LuaError):
    """自定义Lua退出异常"""
    pass


class LuaPath:
    """Lua路径处理适配器"""
    
    def __init__(self, path: Union[str, Path]):
        self._path = Path(path) if isinstance(path, str) else path

    def __str__(self) -> str:
        return str(self._path)

    def add(self, path: str) -> Path:
        """拼接路径"""
        self._path = self._path / path
        return self._path


def python_2_lua(lua_runtime: LuaRuntime, data: Any) -> Any:
    """Python对象转Lua表格"""
    if isinstance(data, (tuple, list, set)):
        table = lua_runtime.table()
        for i, item in enumerate(data, start=1):
            table[i] = item
        return table

    if isinstance(data, dict):
        table = lua_runtime.table()
        for key, value in data.items():
            table[key] = value
        return table

    return data


def output_fix(lua_runtime: LuaRuntime, func: Callable) -> Callable:
    """返回值自动转换装饰器"""
    def wrapper(*args):
        results = func(*args)
        return python_2_lua(lua_runtime, results)
    return wrapper


def output_result(output: Callable, func: Callable, lua_runtime: LuaRuntime) -> Callable:
    """输出结果处理装饰器"""
    def wrapper(*args):
        results = dynamic_call(func, args)

        if isinstance(results, tuple):
            tips = []
            other_results = []
            for result in results:
                if isinstance(result, Tip):
                    tips.append(result)
                else:
                    other_results.append(result)

            for tip in tips:
                output(tip)

            if not other_results:
                return None
            return other_results[0] if len(other_results) == 1 else python_2_lua(lua_runtime, other_results)

        if isinstance(results, Tip):
            output(results)
            return None

        return results
    return wrapper


class LuaDevice:
    """Lua设备操作适配器"""
    
    def __init__(self, device: Any, output: Callable, lua_runtime: LuaRuntime):
        self.device = device
        self.output = output
        self.lua_runtime = lua_runtime

    def update_device(self, device: Any) -> None:
        """更新当前设备"""
        self.device = device

    def __getitem__(self, name: str) -> Callable:
        """获取设备操作方法"""
        if not self.device:
            raise LuaError("请先使用 select_device 选择设备!")

        if not hasattr(self.device, name):
            raise LuaError(f"设备不存在 {name} 操作!")

        return output_result(self.output, getattr(self.device, name), self.lua_runtime)


class LuaImage(Image):
    """Lua图像处理适配器"""
    
    def __init__(self, path: Path, lua_runtime: LuaRuntime):
        super().__init__()
        self.path = path
        self.lua_runtime = lua_runtime
        self.function_maps = {
            "ocr": image_ocr,
            "exact_match": exact_match,
            "simple_fuzzy_match": simple_fuzzy_match,
            "fuzzy_match": fuzzy_match,
            "regex_match": regex_match,
            "template_matching": template_matching,
            "diff_size_template_matching": diff_size_template_matching,
            "open": self._open,
            "crop": self.crop,
        }

    def _open(self, path: str) -> Image | None:
        """打开图像文件"""
        potential_paths = [Path(path), Path(self.path, path)]
        _path = next((p for p in potential_paths if p.exists()), None)
        return self.open(_path) if _path else None

    def __getitem__(self, name: str) -> Any:
        """获取图像处理方法或属性"""
        if func := self.function_maps.get(name):
            return output_fix(self.lua_runtime, func)

        if name == "resolution":
            return self.resolution

        raise LuaError(f"Image 不存在 {name} 操作!")


class LuaScriptRuntime:
    """Lua脚本运行时管理器"""
    
    def __init__(
        self,
        user_input_callback: Callable | None = None,
        notify: Callable | None = None,
    ):
        self.buffer = VirtualFile()
        self.user_input_callback = user_input_callback
        self.notify = notify
        self.lua: LuaRuntime | None = None
        self.path: Path | None = None

    def output_handler(self, message: str = "") -> None:
        """输出处理器"""
        self.buffer.write(f"{message}\n")

    def print_handler(self, *args) -> None:
        """打印处理器"""
        self.output_handler(" ".join(map(str, args)))

    def user_input_handler(self, prompt: str = "", description: str = "") -> Any:
        """用户输入处理器"""
        if self.user_input_callback is None:
            self.notify_handler("脚本使用了用户输入, 但当前运行环境不支持!")
            return ""
        return self.user_input_callback(prompt, description)

    @staticmethod
    def sleep_handler(seconds: float = 1.0) -> None:
        """休眠处理器"""
        time.sleep(seconds)

    def stop_handler(self, message: str = "") -> None:
        """停止脚本处理器"""
        raise LuaExit(message)

    def notify_handler(self, message: str) -> None:
        """通知处理器"""
        if self.notify:
            self.notify(message)

    def set_updata_buffer_handler(self, handler: Callable) -> None:
        """设置缓冲区更新回调"""
        self.buffer.updata_buffer_handler = handler

    def select_device(self, name: str) -> None:
        """选择设备"""
        devices_manager.init_platforms()
        devices_manager.select_devices(name)
        if devices_manager.device is None:
            self.notify(f"尝试切换设备 {name} 但它不存在", title="一个脚本执行错误", severity="error")
        self.lua.globals()["Device"].update_device(devices_manager.device)

    def lua_table(self, python_list: list) -> Any:
        """Python列表转Lua表格"""
        return python_2_lua(self.lua, python_list)

    def init_lua(self, path: str) -> None:
        """初始化Lua环境"""
        self.path = Path(path).parent
        self.lua = LuaRuntime()
        self.buffer.clear()

        globals_table = self.lua.globals()
        
        globals_table["print"] = self.print_handler
        globals_table["input"] = self.user_input_handler
        globals_table["notify"] = self.notify_handler if self.notify else self.output_handler
        globals_table["clear_buffer"] = self.buffer.clear
        globals_table["work_path"] = LuaPath(self.path)
        globals_table["Path"] = LuaPath
        globals_table["lua_table"] = self.lua_table
        globals_table["exit"] = self.stop_handler
        globals_table["python_buffer_file"] = self.buffer
        globals_table["sleep"] = self.sleep_handler
        globals_table["select_device"] = self.select_device
        globals_table["Device"] = LuaDevice(None, self.output_handler, self.lua)
        globals_table["Image"] = LuaImage(self.path, self.lua)
        globals_table["Requests"] = Requests
        
        self.lua.execute(
        """
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
        """
        )

    def run(self, script: str) -> str | Exception | None:
        """执行Lua脚本"""
        try:
            result = self.lua.execute(script)
            if result not in [0, None]:
                self.output_handler(f"程序返回 {result}")
            return None

        except LuaExit as e:
            return None

        except LuaError as e:
            error_msg = "".join(str(e).split(':')[2:])
            formatted_error = f"你的脚本存在错误!\n错误信息：行数: {error_msg}\n"
            self.output_handler(formatted_error)
            return f"脚本语法错误 {e}"

        except Exception as e:
            logger.error(f"发生错误 {e.args[0]}")
            import traceback
            logger.debug("".join(traceback.format_exception(e)))
            self.output_handler("本程序异常!")
            self.output_handler(f"错误 {e if str(e) else '未知错误'}")
            return e if str(e) else "未知错误"