from textual.app import App
from textual.binding import Binding

from .home import HomeScreen
from .run import RunScreen
from .logview import LogPage
from .device import DevicesScreen

import time
import os

import __main__

class TuiApp(App):
    """控制界面"""
    
    exit_flag: int = 0
    
    title = "脚本执行器"
    
    ENABLE_COMMAND_PALETTE = False
    
    CSS = """
    .column {          
        align: center top;
        &>*{ max-width: 100; }        
    }
    Screen .-maximized {
        margin: 1 2;        
        max-width: 100%;
        &.column { margin: 1 2; padding: 1 2; }
        &.column > * {        
            max-width: 100%;           
        }        
    }
    """

    MODES = {
        "home": HomeScreen,
        "devices": DevicesScreen,
        "run": RunScreen,
        "log": LogPage
    }
    DEFAULT_MODE = "home"
    
    BINDINGS = [
        Binding(
            "h",
            "app.switch_mode('home')",
            "主页",
            tooltip="回到主页",
        ),
        Binding(
            "d",
            "app.switch_mode('devices')",
            "设备管理",
            tooltip="选择 && 管理设备",
        ),
        Binding(
            "l",
            "app.switch_mode('log')",
            "日志",
            tooltip="日志页面",
        ),
        Binding(
            "r",
            "app.switch_mode('run')",
            "运行脚本",
            tooltip="运行脚本",
        ),
        Binding(
            "ctrl+a",
            "app.maximize",
            "组件最大化",
            tooltip="组件全屏（如果页面支持）",
        ),
        Binding(
            "ctrl+q",
            "quit",
            "Quit",
            tooltip="退出程序",
            show=False,
            priority=True,
        ),
        Binding("ctrl+c", "help_quit", show=False, system=True),
    ]
    
    def action_maximize(self) -> None:
        if self.screen.is_maximized:
            return
        if self.screen.focused is None:
            self.notify(
                "无需最大化 (尝试按 [b]tab[/b] 键)",
                title="组件最大化",
                severity="warning",
            )
        else:
            if self.screen.maximize(self.screen.focused):
                self.notify(
                    "全屏浏览页面中 按 [b]escape (Esc)[/b] 退出全屏",
                    title="组件最大化",
                )
            else:
                self.notify(
                    "此部件可能未被最大化",
                    title="组件最大化",
                    severity="warning",
                )

    def check_action(self, action: str, parameters: tuple[object, ...]) -> bool | None:
        """Disable switching to a mode we are already on."""
        if (
            action == "switch_mode"
            and parameters
            and self.current_mode == parameters[0]
        ):
            return None
        
        return True
    
    def action_help_quit(self) -> None:
        
        now_time = int(time.time())
        
        if (now_time - self.exit_flag) < 3:
            os._exit(0)
        
        for key, active_binding in self.active_bindings.items():
            if active_binding.binding.action in ("quit", "app.quit"):
                self.notify(
                    f"[b]{key}[/b] 安全退出 或 再按一次 [b]ctrl+c[/b] 强制退出", title="你想退出程序?"
                )
                self.exit_flag = int(time.time())
                return
