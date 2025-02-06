import inspect

from typing import Callable, Any

try:
    from actuator.model import Point
except:
    from model import Point

def dynamic_call(callable: Callable, args: Any= ()):
    
    sig = inspect.signature(callable)
    param_info = sig.parameters
    required_varargs = any(param.kind == inspect.Parameter.VAR_POSITIONAL for param in param_info.values())
    
    if required_varargs: # 原函数不请求任何非可选参数
        return callable(*args)
    
    required_params = [p for p in param_info.values() if p.default == inspect.Parameter.empty]
    
    flat_args = []

    def expand(arg):
        
        if isinstance(arg, (set, tuple)):
            flat_args.extend(arg)
        
        elif isinstance(arg, Point):
            flat_args.append(arg.x)
            flat_args.append(arg.y)
        
        else:
            flat_args.append(arg)
    
    if isinstance(args, (set, tuple)):
        for arg in args:
            expand(arg)
            
    else:
        expand(args)
    
    if len(flat_args) == len(required_params): # 参数一致无需特殊处理
        return callable(*flat_args)

    if len(flat_args) < len(required_params):
        raise Exception(f"参数不足，函数 {callable.__name__} 需要至少 {len(required_params)} 个参数，实际传入 {len(flat_args)} 个参数")

    bound_args = {}
    for i, param_name in enumerate(list(param_info.keys())):
        if i < len(flat_args):
            bound_args[param_name] = flat_args[i]
        elif param_info[param_name].default != inspect.Parameter.empty:
            bound_args[param_name] = param_info[param_name].default
        else:
            raise Exception(f"参数 {param_name} 未传入且无默认值")

    return callable(**bound_args)