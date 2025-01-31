class TokenType:
    """标记类型"""
    NAME = 'NAME'
    """脚本名称"""
    VAR = 'VAR'
    """变量标记"""
    STRING = 'STRING'
    """字符串"""
    NUMBER = 'NUMBER'
    """数字"""
    PLUS = 'PLUS'
    """+"""
    MINUS = 'MINUS'
    """-"""
    MUL = 'MUL'
    """*"""
    DIV = 'DIV'
    """/"""
    PRINT = 'PRINT'
    """打印"""
    IDENTIFIER = 'IDENTIFIER'
    """标识符"""
    ASSIGN = 'ASSIGN'
    """="""
    LPAREN = 'LPAREN'
    """左括号 [ ("""
    RPAREN = 'RPAREN'
    """右括号 ] )"""
    EOF = 'EOF'
    """空字符"""
    DYNAMIC = 'DYNAMIC'
    """dynamic 关键字"""
    LOOP = 'LOOP'
    """循环关键字"""
    LBRACE = 'LBRACE'
    """左大括号 {"""
    RBRACE = 'RBRACE'
    """右大括号 }"""
    COMMA = 'COMMA'
    """逗号,"""
    IF = 'IF'
    """if 关键字"""
    ELSE = 'ELSE'
    """else 关键字"""
    BREAK = 'BREAK'
    """break 关键字"""
    EQ = 'EQ'
    """=="""
    NE = 'NE'
    """!="""
    LT = 'LT'
    """<"""
    GT = 'GT'
    """\>"""
    LE = 'LE'
    """<="""
    GE = 'GE'
    """>="""
    SLEEP = 'SLEEP'
    """sleep"""
    FUNC = 'FUNC'
    """函数关键字"""
    CALL = 'CALL'
    """函数调用"""
    FOREACH = 'FOREACH'
    """迭代"""
    WHILE = 'WHILE'
    """循环"""
    CONTINUE = 'CONTINUE'

class Token:
    """标记类"""
    def __init__(self, token_type: str, value: str):
        self.token_type = token_type
        self.value = value

    def __repr__(self):
        return f'Token({self.token_type}, {self.value})'

class AST:
    """语法树"""
    def __str__(self):
        return self.__class__.__name__

class FunctionCall(AST):
    def __init__(self, func_name: str, args: list[AST]):
        self.func_name = func_name
        self.args = args
        
class UserFunction(AST):
    def __init__(self, func_name: str, body: list[AST], args: list[str]):
        self.func_name = func_name
        self.body = body
        self.args = args
        self.variables = {}

class Foreach(AST):
    def __init__(self, item_name: str, items_value: AST, body: list[AST]):
        self.item_name = item_name
        self.items_value = items_value
        self.body = body
        self.item = None

class VariableDeclaration(AST):
    def __init__(self, var_name: str, value: AST):
        self.var_name = var_name
        self.value = value

class Name(AST):
    def __init__(self, value: AST):
        self.value = value

class String(AST):
    def __init__(self, token: Token):
        self.token = token
        
    def __str__(self):
        return f"String token:{self.token}"

class Number(AST):
    def __init__(self, token: Token):
        self.token = token
    def __str__(self):
        return f"Number token:{self.token}"

class Variable(AST):
    def __init__(self, token: Token):
        self.token = token
    def __str__(self):
        return f"Variable token:{self.token}"

class Print(AST):
    def __init__(self, value: AST):
        self.value = value

class Sleep(AST):
    def __init__(self, value: AST):
        self.value = value

class BinOp(AST):
    def __init__(self, left: AST, op: Token, right: AST):
        self.left = left
        self.op = op
        self.right = right
        
    def __str__(self):
        return f"BinOp {self.mode} :{self.left} {self.op} {self.right}"

class DynamicDeclaration(AST):
    def __init__(self, var_name: str, elements: list[AST] = [], function: FunctionCall = None):
        self.var_name = var_name
        self.elements = elements
        self.function = function
        
class Loop(AST):
    def __init__(self, count: AST, body: list[AST]):
        self.count = count
        self.body = body

class While(AST):
    def __init__(self, count: AST, body: list[AST]):
        self.count = count
        self.body = body

class IfStatement(AST):
    def __init__(self, condition: AST, true_body: list[AST], else_if: list[AST] = [], false_body: list[AST] = []):
        self.condition = condition
        self.true_body = true_body
        self.else_if_body = else_if
        self.false_body = false_body
        self.condition_result = None

class BreakStatement(AST):
    def __init__(self):
        pass


class ContinueStatement(AST):
    def __init__(self):
        pass
    
class BreakException(Exception):
    pass

class ContinueException(Exception):
    pass

class RunException(Exception):
    pass

class Point(AST):
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        
    def __str__(self):
        return f"Point x:{self.x}, y:{self.y}"