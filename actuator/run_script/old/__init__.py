from pathlib import Path
from typing import Callable

import copy, time, inspect

from log import logger
from config import get_config
from consts import devices_manager
from utils.file import FileHelper

from .model import *

def is_float(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

class Lexer:
    """词法分析器"""
    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.line = 1  # 初始化行数计数器
    
    def get_next_token(self) -> Token:
        keywords = {
            "var": TokenType.VAR, "print": TokenType.PRINT, "dynamic": TokenType.DYNAMIC,
            "loop": TokenType.LOOP, "if": TokenType.IF, "else": TokenType.ELSE,
            "break": TokenType.BREAK, "func": TokenType.FUNC, "call": TokenType.CALL,
            "sleep": TokenType.SLEEP, "name": TokenType.NAME, "dyn": TokenType.DYNAMIC,
            "foreach": TokenType.FOREACH, "while": TokenType.WHILE, "continue": TokenType.CONTINUE
        }
        
        while self.pos < len(self.text):
            current_char = self.text[self.pos]

            # 跳过空白符和注释，同时检测换行符
            if current_char.isspace() or current_char == '#':
                if current_char == '\n':
                    self.line += 1  # 遇到换行符，行数增加
                self.pos += 1
                if current_char == '#':  # 跳过注释
                    while self.pos < len(self.text) and self.text[self.pos] != '\n':
                        self.pos += 1
                continue

            # 处理关键字
            for keyword, token_type in keywords.items():
                if self.text.startswith(keyword, self.pos) and (
                    self.pos + len(keyword) == len(self.text) or not self.text[self.pos + len(keyword)].isalnum() and self.text[self.pos + len(keyword)] != '_'
                ):
                    self.pos += len(keyword)
                    return Token(token_type, keyword)
            
            # 处理字符串
            if current_char == '"':
                start_pos = self.pos + 1
                self.pos = self.text.find('"', start_pos)
                if self.pos == -1:
                    raise RunException(f'字符串未闭合，在第 {self.line} 行')
                self.pos += 1
                return Token(TokenType.STRING, self.text[start_pos:self.pos-1])

            # 处理数字
            if current_char.isdigit():
                start_pos = self.pos
                while self.pos < len(self.text) and (self.text[self.pos].isdigit() or self.text[self.pos] == '.'):
                    self.pos += 1
                return Token(TokenType.NUMBER, self.text[start_pos:self.pos])

            # 处理运算符和比较符
            if self.text.startswith(('==', '!=', '<=', '>='), self.pos):
                token = self.text[self.pos:self.pos+2]
                self.pos += 2
                return Token({
                    '==': TokenType.EQ, '!=': TokenType.NE, '<=': TokenType.LE, '>=': TokenType.GE
                }[token], token)
            
            # 单字符标记
            if current_char in '+-*/()[],{}<>=':
                tokens = {
                    '+': TokenType.PLUS, '-': TokenType.MINUS, '*': TokenType.MUL,
                    '/': TokenType.DIV, '(': TokenType.LPAREN, ')': TokenType.RPAREN,
                    '[': TokenType.LPAREN, ']': TokenType.RPAREN, '{': TokenType.LBRACE,
                    '}': TokenType.RBRACE, ',': TokenType.COMMA, '<': TokenType.LT,
                    '>': TokenType.GT, '=': TokenType.ASSIGN
                }
                self.pos += 1
                return Token(tokens[current_char], current_char)

            # 处理标识符
            if current_char.isalpha() or current_char == '_':
                start_pos = self.pos
                while self.pos < len(self.text) and (self.text[self.pos].isalnum() or self.text[self.pos] == '_'):
                    self.pos += 1
                identifier = self.text[start_pos:self.pos]
                return Token(keywords.get(identifier, TokenType.IDENTIFIER), identifier)

            raise RunException(f'非法字符: {current_char} 在第 {self.line} 行')

        return Token(TokenType.EOF, None)


class Parser:
    """语法校验器"""
    def __init__(self, lexer: Lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()
        self.name = ""

    def error(self, code: int, msg: str):
        raise RunException(f"错误码 {code} 出现在 {self.lexer.line} 行 {msg}")

    def consume(self, token_type: str):
        if self.current_token.token_type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error(1, f"错误的语法 需要一个 {token_type} 但是得到了一个 {self.current_token.token_type}")

    def condition(self):
        left = self.expression()
        token = self.current_token
        
        if token.token_type in (TokenType.EQ, TokenType.NE, TokenType.LT, TokenType.GT, TokenType.LE, TokenType.GE):
            self.consume(token.token_type)
            right = self.expression()
            return BinOp(left=left, op=token, right=right)
        
        elif token.token_type in (TokenType.RPAREN):
            return BinOp(left=left, op=Token(TokenType.EQ, '=='), right=None)
        
        else:
            self.error(2, f"无法解析的表达式 得到了非预期的运算符 {token.token_type}")
            
    def if_statement(self):
        self.consume(TokenType.IF)
        self.consume(TokenType.LPAREN)
        condition = self.condition()    # 解析条件
        self.consume(TokenType.RPAREN)
        self.consume(TokenType.LBRACE)
        
        true_body = []
        while self.current_token.token_type != TokenType.RBRACE and self.current_token.token_type != TokenType.EOF:
            true_body.append(self.parse())
        
        self.consume(TokenType.RBRACE)
        
        else_if = []
        false_body = []
        
        while True:   
            if self.current_token.token_type == TokenType.ELSE:
                self.consume(TokenType.ELSE)
                if self.current_token.token_type == TokenType.IF:
                        else_if_body = []
                        self.consume(TokenType.IF)
                        self.consume(TokenType.LPAREN)
                        else_if_condition = self.condition()
                        self.consume(TokenType.RPAREN)
                        self.consume(TokenType.LBRACE)
                        while self.current_token.token_type != TokenType.RBRACE and self.current_token.token_type != TokenType.EOF:
                            else_if_body.append(
                                self.parse()
                            )
                        
                        self.consume(TokenType.RBRACE)
                        else_if.append(
                            IfStatement(
                                else_if_condition,
                                true_body= else_if_body
                            )
                        )
                        
                else:
                    self.consume(TokenType.LBRACE)
                    while self.current_token.token_type != TokenType.RBRACE and self.current_token.token_type != TokenType.EOF:
                        false_body.append(self.parse())
                    self.consume(TokenType.RBRACE)
                
            else:
                break
        
        return IfStatement(condition, true_body, else_if, false_body)
    
    def variable_declaration(self):
        self.consume(TokenType.VAR)
        var_name = self.current_token.value  # 获取变量名
        self.consume(TokenType.IDENTIFIER)
        self.consume(TokenType.ASSIGN)
        value = self.expression()  # 获取赋值
        return VariableDeclaration(var_name, value)  # 返回变量声明节点

    def dynamic_declaration(self):
        self.consume(TokenType.DYNAMIC)
        var_name = self.current_token.value
        self.consume(TokenType.IDENTIFIER)
        self.consume(TokenType.ASSIGN)

        if self.current_token.token_type == TokenType.LPAREN: 
            elements = self.parse_nested_list()
            return DynamicDeclaration(var_name, elements=elements)

        elif self.current_token.token_type == TokenType.CALL:  # 如果是函数调用
            return DynamicDeclaration(var_name, function=self.call_statement())

        elif self.current_token.token_type == TokenType.IDENTIFIER:  # 如果是一个标识符
            return DynamicDeclaration(var_name, elements=self.expression())
    
    def parse_nested_list(self):
        """解析嵌套列表"""
        elements = []  # 存储列表元素
        self.consume(TokenType.LPAREN)
        
        while self.current_token.token_type != TokenType.RPAREN:
            if self.current_token.token_type == TokenType.LPAREN:  # 嵌套列表
                elements.append(self.parse_nested_list())  # 递归解析嵌套列表
                
            elif self.current_token.token_type == TokenType.COMMA:  # 跳过逗号
                self.consume(TokenType.COMMA)
            else:
                elements.append(self.expression())  # 添加单个表达式

        self.consume(TokenType.RPAREN)
        return elements

    def factor(self):
        token = self.current_token
        if token.token_type == TokenType.NUMBER:
            self.consume(TokenType.NUMBER)
            return Number(token)
        elif token.token_type == TokenType.STRING:
            self.consume(TokenType.STRING)
            return String(token)  # 返回字符串节点
        elif token.token_type == TokenType.IDENTIFIER:
            self.consume(TokenType.IDENTIFIER)
            return Variable(token)
        elif token.token_type == TokenType.LPAREN:           
            self.consume(TokenType.LPAREN)
            node = self.expression()
            self.consume(TokenType.RPAREN)  # consume the closing parenthesis
            return node
    
    def expression(self):
        node = self.term()
        while self.current_token.token_type in (TokenType.PLUS, TokenType.MINUS, TokenType.MUL, TokenType.DIV):
            token = self.current_token
            if token.token_type == TokenType.PLUS:
                self.consume(TokenType.PLUS)
            elif token.token_type == TokenType.MINUS:
                self.consume(TokenType.MINUS)
            elif token.token_type == TokenType.MUL:
                self.consume(TokenType.MUL)
            elif token.token_type == TokenType.DIV:
                self.consume(TokenType.DIV)
            
            node = BinOp(left=node, op=token, right=self.term())
            
        return node

    def break_statement(self):
        self.consume(TokenType.BREAK)  # consume break
        return BreakStatement()
    
    def function_call(self):
        func_name = self.current_token.value
        self.consume(TokenType.IDENTIFIER)
        self.consume(TokenType.LPAREN)
        args = []
        while self.current_token.token_type != TokenType.RPAREN:
            args.append(self.expression())
            if self.current_token.token_type == TokenType.RPAREN:
                break
            self.consume(TokenType.COMMA)
        self.consume(TokenType.RPAREN)
        return FunctionCall(func_name, args)
    
    def term(self):
        token = self.current_token
        if token.token_type == TokenType.NUMBER:
            self.consume(TokenType.NUMBER)
            return Number(token)
        elif token.token_type == TokenType.IDENTIFIER:
            self.consume(TokenType.IDENTIFIER)
            return Variable(token)
        elif token.token_type == TokenType.STRING:
            self.consume(TokenType.STRING)
            return String(token)  # 返回字符串节点
        elif token.token_type == TokenType.LPAREN:
            self.consume(TokenType.LPAREN)
            node = self.expression()
            self.consume(TokenType.RPAREN)
            return node

    def print_statement(self):
        self.consume(TokenType.PRINT)
        self.consume(TokenType.LPAREN)
        value = self.expression()  # 获取要打印的值
        self.consume(TokenType.RPAREN)
        return Print(value)  # 返回打印语句节点

    def loop_statement(self):
        self.consume(TokenType.LOOP)
        count = self.expression()  # 获取循环次数
        self.consume(TokenType.LBRACE)
        body = []
        while self.current_token.token_type != TokenType.RBRACE and self.current_token.token_type != TokenType.EOF:
            body.append(self.parse())  # 解析循环体
            
        self.consume(TokenType.RBRACE)
        return Loop(count, body)  # 返回循环节点
    
    def while_statement(self):
        self.consume(TokenType.WHILE)
        count = self.expression()  # 获取循环条件
        self.consume(TokenType.LBRACE)
        body = []
        while self.current_token.token_type != TokenType.RBRACE and self.current_token.token_type != TokenType.EOF:
            body.append(self.parse())  # 解析循环体
            
        self.consume(TokenType.RBRACE)
        return While(count, body)  # 返回循环节点
    
    def func_statement(self):
        self.consume(TokenType.FUNC)
        func_name = self.current_token.value
        self.consume(TokenType.IDENTIFIER)
        
        elements = []
        if self.current_token.token_type == TokenType.LPAREN:
            self.current_token = self.lexer.get_next_token()
            while self.current_token.token_type != TokenType.RPAREN:
                elements.append(self.expression())
                
                if self.current_token.token_type == TokenType.RPAREN:
                    break
                
                self.consume(TokenType.COMMA)
                    
            self.consume(TokenType.RPAREN)
        
        self.consume(TokenType.LBRACE)
        body = []
        while self.current_token.token_type != TokenType.RBRACE and self.current_token.token_type != TokenType.EOF:
            body.append(self.parse())
            
        self.consume(TokenType.RBRACE)
        return UserFunction(func_name, body, elements)

    def foreach_statement(self):
        self.consume(TokenType.FOREACH)
        self.consume(TokenType.LPAREN)
        
        item_name = self.current_token.value
        self.consume(TokenType.IDENTIFIER)
        
        self.consume(TokenType.COMMA)
        
        items_value = self.expression()
        
        self.consume(TokenType.RPAREN)
        
        self.consume(TokenType.LBRACE)
        body = []
        while self.current_token.token_type != TokenType.RBRACE and self.current_token.token_type != TokenType.EOF:
            body.append(self.parse())
            
        self.consume(TokenType.RBRACE)
        return Foreach(item_name, items_value, body)

    def call_statement(self):
        self.consume(TokenType.CALL)
        return self.function_call()
    
    def sleep_statement(self):
        self.consume(TokenType.SLEEP)
        self.consume(TokenType.LPAREN)
        count = self.expression()
        self.consume(TokenType.RPAREN)
        return Sleep(count)
    
    def continue_statement(self):
        self.consume(TokenType.CONTINUE)  # consume continue
        return ContinueStatement()
    
    def name_statement(self):
        self.consume(TokenType.NAME)
        self.name = Name(self.term().token.value).value
        return Name(self.name)
    
    def parse(self):
        if self.current_token.token_type == TokenType.NAME:
            return self.name_statement()
        elif self.current_token.token_type == TokenType.VAR:
            return self.variable_declaration()
        elif self.current_token.token_type == TokenType.DYNAMIC:
            return self.dynamic_declaration()
        elif self.current_token.token_type == TokenType.IF:
            return self.if_statement()
        elif self.current_token.token_type == TokenType.PRINT:
            return self.print_statement()
        elif self.current_token.token_type == TokenType.LOOP:
            return self.loop_statement()
        elif self.current_token.token_type == TokenType.WHILE:
            return self.while_statement()
        elif self.current_token.token_type == TokenType.BREAK:
            return self.break_statement()
        elif self.current_token.token_type == TokenType.SLEEP:
            return self.sleep_statement()
        elif self.current_token.token_type == TokenType.FUNC:
            return self.func_statement()
        elif self.current_token.token_type == TokenType.CALL:
            return self.call_statement()
        elif self.current_token.token_type == TokenType.FOREACH:
            return self.foreach_statement()
        elif self.current_token.token_type == TokenType.CONTINUE:
            return self.continue_statement()
        
        self.error(3, f"错误的语法结构体 {self.current_token.token_type}")

def is_nested(args):
    if isinstance(args, (list, tuple)):
        return any(isinstance(item, (list, tuple)) for item in args)
    return False


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
        
        elif isinstance(arg, Point):
            flat_args.extend([arg.x, arg.y])
        
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
        result = callable(*args, **kwargs)
        if isinstance(result, tuple):
            output(result[0])
            return result[1:]
        else:
            output(result)
            
    return wrapper

def pathSplicing(*paths: list) -> str:
    """路径拼接"""
    paths = [str(path) for path in paths]
    return "/".join(paths)

def formatString(*paths: list) -> str:
    """格式化字符串"""
    paths = [str(path) for path in paths]
    return "".join(paths)

class InternalMethods:
    
    def __init__(
        self,
        device,
        path: Path,
        output: Callable,
        notify: Callable
    ) -> None:
        
        self.device = device
        self.path = path
        self.output = output
        self.notify = notify
        
        self.methods_maps = {
            "select_device": self.select_device,
            "fileMove" : FileHelper.file_move,
            "fileRename" : FileHelper.file_rename,
            "folderCreate" : FileHelper.folder_create,
            "pathSplicing" : pathSplicing,
            "formatString" : formatString,
            
        }
    
    def select_device(self, name: str):
        devices_manager.init_platforms()
        devices_manager.select_devices(name)
        
        if devices_manager.device == None:
            self.notify(f"尝试切换设备 {name} 但它不存在", title="一个脚本执行错误", severity="error")
            
        self.device = devices_manager.device
    
    def get(self, name: str):
        
        if method := self.methods_maps.get(name):
            return method
        
        if not self.device:
            raise RunException("请先使用 call select_device(设备名称) 选择设备 !")
        
        if hasattr(self.device, name):
            return output_result(self.output, getattr(self.device, name))
        
        raise RunException(f"设备不存在 {name} 操作 !")

class Interpreter:
    """解释器"""

    def __init__(
        self,
        parser: Parser,
        path: Path,
        updata_buffer_handler: Callable,
        notify: Callable,
    ):
        self.path = path.parent
        self.parser = parser
        self.variables = {"work_path": path}
        self.user_func: dict[str, UserFunction] = {}

        self.used_func: list[UserFunction] = []
        self.foreach: list[Foreach] = []
        self.updata_buffer_handler: Callable = updata_buffer_handler
        self.internal_methods = InternalMethods(devices_manager.device, path, updata_buffer_handler, notify)
        self.stop = False

    def get_variables(self, name: str):
        """获取变量值"""
        # 在 foreach 环境中，优先使用当前迭代项
        if self.foreach and name == self.foreach[-1].item_name:
            return self.foreach[-1].item

        # 在函数环境中优先使用函数局部变量
        if self.used_func:
            if variable := self.used_func[-1].variables.get(name):
                return variable

        # 全局变量兜底
        return self.variables.get(name, 0)

    def set_variables(self, name: str, value):
        """设置变量值"""
        if self.used_func:
            # 如果是全局变量，直接更新；否则更新当前函数的局部变量
            if name in self.variables:
                self.variables[name] = value
            else:
                self.used_func[-1].variables[name] = value
        else:
            self.variables[name] = value

    def process_nested_elements(self, elements):
        """递归处理嵌套列表"""
        processed = []
        
        if not isinstance(elements, list):
            return elements
        
        for element in elements:
            if isinstance(element, list):  # 如果是列表，递归处理
                processed.append(self.process_nested_elements(element))
            else:
                processed.append(self.visit(element))  # 对单个元素进行访问处理
        return processed

    def visit(self, node: AST):
        """访问 AST 节点"""
        if self.stop:
            logger.info(f"脚本: {self.parser.name} 被强制结束")
            raise BreakException()

        # 处理不同类型的节点
        if isinstance(node, Number):
            value = node.token.value
            return float(value) if "." in str(value) else int(value)

        if isinstance(node, String):
            return node.token.value

        if isinstance(node, Variable):
            return self.get_variables(node.token.value)

        if isinstance(node, BinOp):
            return self._process_bin_op(node)

        if isinstance(node, Print):
            value = self.visit(node.value)
            self.updata_buffer_handler(f"{value}\n")
            logger.debug(f"脚本打印: {value}")
            return

        if isinstance(node, Sleep):
            return self._process_sleep(node)

        if isinstance(node, IfStatement):
            return self._process_if_statement(node)

        if isinstance(node, VariableDeclaration):
            value = self.visit(node.value)
            self.set_variables(node.var_name, value)
            return value

        if isinstance(node, DynamicDeclaration):
            return self._process_dynamic_declaration(node)

        if isinstance(node, Foreach):
            return self._process_foreach(node)

        if isinstance(node, FunctionCall):
            return self._process_function_call(node)

        if isinstance(node, UserFunction):
            self.user_func[node.func_name] = node

        if isinstance(node, While):
            return self._process_while(node)
        
        if isinstance(node, Loop):
            return self._process_loop(node)

        if isinstance(node, Point):
            return self._process_point(node)
        
        if isinstance(node, BreakStatement):
            raise BreakException()

        if isinstance(node, ContinueStatement):
            raise ContinueException()
        
        return node

    def _process_point(self, node: Point):
        return (int(node.x), int(node.y))
    
    def _process_function_call(self, node: FunctionCall):
        if func := self.user_func.get(node.func_name):
            
            func = copy.deepcopy(func)
            
            if len(func.args) != len(node.args):
                raise Exception(f"函数 {node.func_name} 参数数量不匹配，期望 {len(func.args)}，实际 {len(node.args)}")
            
            for func_arg, call_arg in zip(func.args, node.args):
                
                if call_arg.token.value.isdigit():
                    func.variables[func_arg.token.value] = int(call_arg.token.value)
                        
                elif is_float(call_arg.token.value):
                    func.variables[func_arg.token.value] = float(call_arg.token.value)
                        
                elif isinstance(call_arg, Variable):
                    func.variables[func_arg.token.value] = self.get_variables(call_arg.token.value)
                    
                else:
                    func.variables[func_arg.token.value] = call_arg.token.value
            
            self.used_func.append(func)
            
            try:
                for body_node in func.body:
                    self.visit(body_node)
            except BreakException:
                pass
                
            self.used_func.remove(func)
            logger.debug(f"执行函数 {node.func_name} 完成, 栈深度 {len(self.used_func)}")
            return
        
        mapping = {value: key for key, value in get_config().mapping.items()}
        
        func_name = mapping.get(node.func_name, node.func_name)
        
        if func := self.internal_methods.get(func_name):
            args = [self.visit(arg) for arg in node.args]
            try:
                dynamic_call(func, args)
                    
            except Exception as e:
                logger.warning(f"函数 {node.func_name} 执行错误 {e}!")
                    
            return
        
        logger.warning(f"不存在的函数 {node.func_name} !")
        
    
    def _process_foreach(self, node: Foreach):
        self.foreach.append(node)
        itmes = self.visit(node.items_value)
            
        if isinstance(itmes, float):
            itmes = int(itmes)
        
        try:
            if isinstance(itmes, int):
                for item in range(0, itmes):
                    self.foreach[-1].item = item
                    for body in node.body:
                        try:
                            self.visit(body)
                        except ContinueException:
                            continue
                            
            elif isinstance(itmes, (list, tuple, set)):
                for item in itmes:
                    self.foreach[-1].item = item
                    for body in node.body:
                        try:
                            self.visit(body)
                        except ContinueException:
                            continue
            else:
                logger.warning(f"不可迭代的对象 {itmes} 循环将不会执行!")
                
        except BreakException:
            pass
                        
        self.foreach.remove(node)
    
    
    def _process_loop(self, node: Loop):
        try: 
            for _ in range(int(self.visit(node.count))):
                for body_node in node.body:
                    try:
                        self.visit(body_node)
                    except ContinueException:
                        continue
                    
        except BreakException:
            pass

    
    def _process_while(self, node: While):
        try:
            while self.visit(node.count):
                for body_node in node.body:
                    try:
                        self.visit(body_node)
                    except ContinueException:
                        continue
                    
        except BreakException:
            pass
    
    def _process_bin_op(self, node: BinOp):
        """处理二元操作符"""
        left, right = self.visit(node.left), self.visit(node.right)
        
        if isinstance(left, str) or  isinstance(right, str) and node.op == TokenType.PLUS:
            return f"{left} {right}"
        
        # 向量操作支持
        if isinstance(left, (list, tuple, Point)) and isinstance(right, (list, tuple, Point)):
            return self._process_vector_operations(node.op.token_type, left, right)

        # 处理单值判断
        if not right and left and right is None:
            if isinstance(left, (list, tuple)):
                return all(left)
            return True

        # 标量操作支持
        return self._process_scalar_operations(node.op.token_type, left, right)

    def _process_vector_operations(self, op_type, left, right):
        """处理向量操作"""
        
        operations = {
            TokenType.PLUS: lambda: [l + r for l, r in zip(left, right)],
            TokenType.MINUS: lambda: [l - r for l, r in zip(left, right)],
            TokenType.MUL: lambda: [l * r for l, r in zip(left, right)],
            TokenType.DIV: lambda: [l / r if r != 0 else logger.warning("0 作为除数是无意义的") or 0 for l, r in zip(left, right)],
            TokenType.EQ: lambda: [l == r for l, r in zip(left, right)],
            TokenType.NE: lambda: [l != r for l, r in zip(left, right)],
            TokenType.LT: lambda: [l < r for l, r in zip(left, right)],
            TokenType.GT: lambda: [l > r for l, r in zip(left, right)],
            TokenType.LE: lambda: [l <= r for l, r in zip(left, right)],
            TokenType.GE: lambda: [l >= r for l, r in zip(left, right)],
        }
        
        result = operations.get(op_type, lambda: RunException(f"未知运算符: {op_type}"))()
        
        if not op_type in (TokenType.PLUS, TokenType.MINUS, TokenType.MUL, TokenType.DIV):
            
            logger.debug(f"计算 {left} {op_type} {right}")
            
            if False in result:
                return False
                
            return True
        
        logger.debug(f"判断 {left} {op_type} {right}")
        
        return result

    def _process_scalar_operations(self, op_type, left, right):
        """处理标量操作"""
        operations = {
            TokenType.PLUS: lambda: left + right,
            TokenType.MINUS: lambda: left - right,
            TokenType.MUL: lambda: left * right,
            TokenType.DIV: lambda: left / right if right != 0 else logger.warning("0 作为除数是无意义的") or 0,
            TokenType.EQ: lambda: left == right,
            TokenType.NE: lambda: left != right,
            TokenType.LT: lambda: left < right,
            TokenType.GT: lambda: left > right,
            TokenType.LE: lambda: left <= right,
            TokenType.GE: lambda: left >= right,
        }
        
        if not op_type in (TokenType.PLUS, TokenType.MINUS, TokenType.MUL, TokenType.DIV):
            
            logger.debug(f"计算 {left} {op_type} {right}")
            
        else:
            logger.debug(f"判断 {left} {op_type} {right}")
        
        return operations.get(op_type, lambda: RunException(f"未知运算符: {op_type}"))()

    def _process_sleep(self, node: Sleep):
        """处理延迟"""
        value = self.visit(node.value)
        logger.debug(f"延迟 {value}s")
        for _ in range(int(value * 100)):  # 以 0.01 秒为间隔延迟
            if self.stop:
                break
            time.sleep(0.01)
        return value

    def _process_if_statement(self, node: IfStatement):
        """处理 if 语句"""
        condition = self.visit(node.condition)
        
        body = node.true_body if condition else (node.false_body or [])
        
        for else_if_node in node.else_if_body:
            if self.visit(else_if_node.condition):
                body = else_if_node.true_body
                break
        
        for stmt in body:
            self.visit(stmt)

    def _process_dynamic_declaration(self, node: DynamicDeclaration):
        """处理动态声明"""
        if node.elements:
            elements = self.process_nested_elements(node.elements)
            
            elements = self.visit(elements)
            
            self.set_variables(node.var_name, elements)
            
            return elements

        mapping = {value: key for key, value in get_config().mapping.items()}
        
        func_name = mapping.get(node.function.func_name, node.function.func_name)
        
        if node.function and (func := self.internal_methods.get(func_name)):
            
            args = [self.visit(arg) for arg in node.function.args]
            try:
                result = dynamic_call(func, args)
                self.set_variables(node.var_name, result)
                return result
            except Exception as e:
                logger.warning(f"函数 {node.function.func_name} 执行错误: {e}")
                return None
            
        logger.warning(f"不存在的函数 {node.function.func_name}")
        
        return None

    def interpret(self):
        """解释器入口"""
        try:
            while self.parser.current_token.token_type != TokenType.EOF:
                self.visit(self.parser.parse())
        except BreakException:
            pass


class ScriptFileRuntime:
    def __init__(
        self, 
        user_input_callback: Callable = None,
        notify: Callable = None
    ):
        self.name = ""
        
        self.updata_buffer_handler: Callable = None
        self.user_input_callback: Callable = user_input_callback
        self.notify: Callable = notify
    
    def run(self, script: str, name: str, path: Path):
        
        script = f"name \"{name}\"\n" + script
        
        try:
            return self.run_script(script, name, path.parent)
        except Exception as e:
            return e
    
    def run_script(self, script: str, name: str, path: Path):
        lexer = Lexer(script)
        parser = Parser(lexer)
        self.interpreter = Interpreter(parser, path, self.updata_buffer_handler, self.notify)
        
        parser.parse()
            
        if parser != "":
            self.name = parser.name
        
        logger.debug(f"脚本 {name} 执行开始")
        try:
            self.interpreter.interpret()
        
        except RunException as e:
            logger.error(f"发生错误 {e.args[0]}")
            self.updata_buffer_handler(f"发生错误 {e.args[0]}\n")
            return f"{e.args[0]}"
        
        except Exception as e:
            import traceback
            logger.error(f"发生错误 {e.args[0]}")
            error_message = "".join(traceback.format_exception(e))
            logger.debug(error_message)
            logger.debug(f"错误来源 行数: {self.interpreter.parser.lexer.line}")
            
            self.updata_buffer_handler(f"发生错误 {e.args[0]}\n")
            self.updata_buffer_handler(f"错误来源 行数: {self.interpreter.parser.lexer.line}")
            
            return f"{e.args[0]}\n行数: {self.interpreter.parser.lexer.line}"
            
        logger.debug(f"脚本 {name} 执行完毕")
    
    def set_updata_buffer_handler(self, handler: Callable):
        self.updata_buffer_handler = handler