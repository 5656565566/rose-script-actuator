from typing import Type
from abc import ABC, abstractmethod

import inspect

kind_translation_str = {
    "POSITIONAL_ONLY": "仅限位置参数",
    "POSITIONAL_OR_KEYWORD": "位置或关键字参数",
    "VAR_POSITIONAL": "可变位置参数",
    "KEYWORD_ONLY": "仅限关键字参数",
    "VAR_KEYWORD": "可变关键字参数",
}

def get_parameters_details(func):
    
    message = f"函数简介: {func.__doc__}".replace("Args", "参数").replace("Returns", "返回值") if func.__doc__ else ""
    
    sig = inspect.signature(func)
    details = []
    
    for name, param in sig.parameters.items():
        default = param.default if param.default is not param.empty else "无默认值"
        param_type = param.annotation.__name__ if param.annotation is not param.empty else "任意类型"
        kind= kind_translation_str.get(str(param.kind).split(".")[-1])
        
        details.append(f"{name} 类型:{param_type} 默认值:{default} 如何传递:{kind}")
    
    if not details:
        return "无参数"
    
    return message + "\n".join(details)

class Platform(ABC):
    
    devices: list[Type["Devices"]] = []
    
    @abstractmethod
    def __init__(self):
        raise NotImplementedError
    
    @property
    @abstractmethod
    def platform_name(self):
        return __class__.__name__
    
    @property
    @abstractmethod
    def platform_decription(self):
        raise NotImplementedError
    
    @abstractmethod
    def get_all_device(self):
        raise NotImplementedError
    
    @abstractmethod
    def select_deivce(self, name: str):
        raise NotImplementedError

            
platforms: list[Type[Platform]] = []

def register_platform(platform: Type[Platform]):
    platforms.append(platform)
    
    
class Devices:
    
    def __init__(self, name: str):
        self.name = name
    
    def __call__(self, *args):
        _args = list(args)
        
        function_name = _args.pop(0) if _args else None
        if function_name is None:
            return False, None
        
        if function_name[0] == "_":
            return False, None
        
        if hasattr(self, function_name):
            func = getattr(self, function_name)
            
            try:
                if _args:
                    return True, func(args)
                return True, func()
            except:
                
                return False, f"调用 {function_name} 错误\n{get_parameters_details(func)}"