from rich.syntax import Syntax
from textual import work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import ScrollableContainer, Grid
from textual.screen import ModalScreen, Screen
from textual.widgets import Button, Static, Footer, Markdown, Input
from textual.worker import Worker

from pathlib import Path
from dataclasses import dataclass

import threading
import ctypes
import time

from log import logger
from run_script import LuaScriptRuntime, ScriptFileRuntime
from typing import Callable
from consts import threadings, devices_manager # TODO 实现多同类设备运行

class LogScreen(ModalScreen):
    DEFAULT_CSS = """
    LogScreen {
        #code {
            border: heavy $accent;
            margin: 2 4;
            scrollbar-gutter: stable;
            Static {
                width: auto;
            }
        }
        #code.simple-view {
            border: none;  /* 移除边框 */
            margin: 0 0;   /* 减小边距 */
        }
    }
    """
    BINDINGS = [
        ("escape", "dismiss", "关闭窗口"),
        ("s", "toggle_view", "切换复制模式"),
    ]

    def __init__(self, title: str, message: str, log_dismiss_callback: Callable) -> None:
        super().__init__()
        self.message = message
        self.title = title
        self.use_simple_view = False
        self.log_dismiss_callback = log_dismiss_callback

    def dismiss(self, result = None):
        self.log_dismiss_callback()
        return super().dismiss(result)
    
    def compose(self) -> ComposeResult:
        with ScrollableContainer(id="code"):
            yield self._create_code_widget()

    def _create_code_widget(self):
        if self.use_simple_view:
            return Static(self.message, expand=True)
        else:
            return Static(
                Syntax(
                    self.message,
                    lexer="log",
                    indent_guides=True,
                    line_numbers=True
                ),
                expand=True,
            )

    def update_log(self, message: str) -> None:
        self.message = message
        code_container = self.query_one("#code")
        code_container.remove_children()
        code_container.mount(self._create_code_widget())
    
    def action_toggle_view(self) -> None:
        self.use_simple_view = not self.use_simple_view
        code_container = self.query_one("#code")
        
        # 切换 CSS 类
        code_container.set_class(self.use_simple_view, "simple-view")
        
        # 更新内容组件
        code_container.remove_children()
        code_container.mount(self._create_code_widget())
        
        # 更新边框标题状态（仅在非简单模式显示）
        if not self.use_simple_view:
            code_container.border_title = self.title
            code_container.border_subtitle = "按 [b]escape (Esc)[/b] 退出 | 按 [b]s[/b] 切换模式 按住 Shift 鼠标选择文本按 [b]Ctrl + C[/b] 复制"
        else:
            code_container.border_title = ""
            code_container.border_subtitle = ""

    def on_mount(self):
        code_widget = self.query_one("#code")
        code_widget.border_title = self.title
        code_widget.border_subtitle = "按 [b]escape (Esc)[/b] 退出 | 按 [b]s[/b] 切换模式"


class InputModal(ModalScreen[str]):
    """用户输入弹窗"""

    DEFAULT_CSS = """
    InputModal {
        align: center middle;
    }

    InputModal > Grid {
        grid-size: 2;
        grid-gutter: 1;
        width: 60;
        height: 16;
        border: thick $accent;
        background: $surface;
    }

    InputModal > Grid > Markdown {
        width: 1fr;
        column-span: 2;
        background: transparent;
    }

    InputModal > Grid > Input {
        column-span: 2;
    }

    InputModal > Grid > Button {
        width: 100%;
    }
    """

    def __init__(self, description: str, prompt: str) -> None:
        super().__init__()
        self.description = description
        self.prompt = prompt

    def compose(self) -> ComposeResult:
        """布局弹窗组件"""
        with Grid():
            yield Markdown(self.description, id="description")
            yield Input(placeholder=self.prompt, id="input")
            yield Button("确认", variant="primary", id="confirm")
            yield Button("取消", variant="error", id="cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """处理按钮点击事件"""
        if event.button.id == "confirm":
            input_widget = self.query_one("#input", Input)
            self.dismiss(input_widget.value)
        else:
            self.dismiss(None)

@dataclass
class InputTask:
    description: str = ""
    prompt: str = ""
    _time: float = time.time()
    
    def __hash__(self):
        return hash(self._time)

class RunScreen(Screen):
    DEFAULT_CSS = """
    RunScreen {
        width: 100%;
        height: 1fr;
        overflow-y: auto;
    }

    RunScreen > #file-list {
        overflow-x: auto;
    }

    .file-btn {
        background: #4CAF50;
        margin: 1;        /* 移除默认外边距 */
        width: 100%;
    }

    .file-btn:hover {
        background: #45a049;
    }

    .file-btn:focus {
        color: white;
    }

    """
    BINDINGS = [
        Binding(
            "c",
            "show_log",
            "显示日志",
            tooltip="显示运行时通过 print 打印的日志",
        ),
        Binding(
            "r",
            "get_script_list",
            "刷新",
            tooltip="重新获取脚本列表",
        ),
        Binding(
            "l",
            "clear_log",
            "清空日志",
            tooltip="清空日志",
        ),
        Binding(
            "s",
            "stop_tasks",
            "停止所有脚本",
            tooltip="停止所有脚本",
        )
    ]

    def __init__(self, name=None, id=None, classes=None):
        self.lua_files = self.get_script_list()
        self.script_message: str = ""
        
        self.script_tasks: dict[str, Worker] = {}
        self.input_tasks: dict[InputTask, str] = {}
        
        super().__init__(name, id, classes)

        self.lua = LuaScriptRuntime(
            notify= self.notify,
            user_input_callback= self.user_input_handler
        )
        
        self.old = ScriptFileRuntime(
            notify= self.notify,
            user_input_callback= self.user_input_handler
        )
        
        self.lua.set_updata_buffer_handler(self.update_log)
        self.old.set_updata_buffer_handler(self.update_log)
        
        self.log_ui = None
        
        self.user_input_loop()
    
    def user_input_handler(self, description: str, prompt: str) -> str:
        
        input_task = InputTask(description, prompt)
        
        self.input_tasks[input_task] = True
        # 添加信息到队列
        
        while self.input_tasks.get(input_task, True) == True: # 等待回复
            time.sleep(1)
        
        return self.input_tasks.pop(input_task)
    
    @work(thread=True)
    async def user_input_loop(self) -> str:
        """弹出用户输入弹窗并保存输入内容到队列"""
        
        while True:
            for input_task in self.input_tasks.keys():
                
                if self.input_tasks[input_task] != True:
                    continue
                
                result = self.app.call_from_thread(self.app.push_screen_wait, InputModal(input_task.description, input_task.prompt))
                
                self.input_tasks[input_task] = result
                
            time.sleep(1)
    
    def compose(self) -> ComposeResult:
        """动态生成文件列表界面"""

        yield Footer()
        yield Markdown("# 选择脚本")

        if not self.lua_files:
            yield Static("[red]未找到任何脚本文件[/red] 使用 [b]H[/b] 返回主页", classes="error")
            return

        with ScrollableContainer(id="file-list", can_maximize=True):
            for file in self.lua_files:
                yield Button(
                    file.name,
                    classes="file-btn",
                    action=f"screen.run_script({str(file)!r})",
                )
    
    def action_get_script_list(self) -> None:
        """获取并刷新当前目录下的Lua脚本列表"""
        try:
            self.lua_files = sorted(
                self.get_script_list(),
                key=lambda f: f.name.lower()
            )
            
            self.refresh()

            list_container = self.query_one("#file-list")
            
            list_container.remove_children()
            if self.lua_files:
                    for file in self.lua_files:
                        list_container.mount(
                            Button(
                                file.name,
                                classes="file-btn",
                                action=f"screen.run_script({str(file)!r})",
                            )
                        )
            list_container.refresh(layout=True)
            self.notify("成功刷新了脚本列表")
            
        except Exception as e:
            self.notify(
                f"未知错误：{str(e)}", 
                title="刷新失败", 
                severity="error"
            )
    
    @work(thread=True)
    def run_lua_scripts(self, code: str, name: str, path: str):
        
        def _not_safe_thread_run():
            if err := self.lua.run(code):
                self.notify(f"脚本执行错误 {err} 详情可见日志", severity="error")
                
            self.notify(f"脚本 {name} 执行完毕")
            self.script_tasks.pop(path)
            threadings.remove(thread)
            
        thread = threading.Thread(target=_not_safe_thread_run)
        threadings.append(thread)
        thread.start()
    
    @work(thread=True)
    def run_old_scripts(self, code: str, name: str, path: str):
        
        def _not_safe_thread_run():
            if err := self.old.run(code, name, Path(path)):
                self.notify(f"脚本执行错误 {err} 详情可见日志", severity="error")
                
            self.notify(f"脚本 {name} 执行完毕")
            self.script_tasks.pop(path)
            threadings.remove(thread)
        
        thread = threading.Thread(target=_not_safe_thread_run)
        threadings.append(thread)
        thread.start()
    
    async def action_run_script(self, path: str):
        """处理按钮点击事件"""
        
        _path = Path(path)
        
        if not _path.exists():
            self.notify(f"文件不存在: {path}", severity="error")
            return
        
        if self.script_tasks.get(path):
            self.notify(f"脚本: {_path.name} 已经在运行中了...", severity="warning")
            return
        
        logger.info(f"尝试执行脚本 {_path.name}")
        
        self.notify(f"脚本 {_path.name} 开始运行")
        
        if code := self.get_code(path):
            
            if "lua" in _path.name:
                self.lua.init_lua()
                self.script_tasks[path] = self.run_lua_scripts(code, _path.name, path)
                
            if "txt" in _path.name:
                self.script_tasks[path] = self.run_old_scripts(code, _path.name, path)
            
        else:
            self.log.warning(f"无法读取文件: {path}")
            self.notify("文件读取失败", severity="error")
    
    def action_stop_tasks(self):
        for task in self.script_tasks.values():
            task.cancel() # 取消尚未开始的任务
            
        for threading in threadings:
            thread_id = threading.ident
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, ctypes.py_object(SystemExit))
        
        self.notify(f"强行停止了运行中的 {len(threadings)} 个任务")
        
        threadings.clear()
        self.script_tasks.clear()
    
    def get_code(self, source_file: str) -> str | None:
        """获取脚本文件"""
        try:
            with open(source_file, "rt", encoding="utf-8") as file:
                return file.read()
        except Exception:
            return None

    @staticmethod
    def get_script_list() -> list[Path]:
        """获取脚本文件列表"""
        lua_scripts = list(Path.cwd().glob("*.lua")) # lua 版本
        old_scripts = list(Path.cwd().glob("*.txt")) # 旧版本
        
        return lua_scripts + old_scripts

    def action_clear_log(self):
        self.notify("日志清空 !")
        self.script_message = ""
    
    def update_log(self, message: str):
        self.script_message += message
        
        if self.log_ui is not None:
            self.app.call_from_thread(self.log_ui.update_log, self.script_message)
    
    def log_dismiss_callback(self):
        self.log_ui = None
    
    def action_show_log(self):
        """显示运行时日志"""
        
        self.log_ui = LogScreen("日志", self.script_message, self.log_dismiss_callback)
        self.app.push_screen(self.log_ui)
