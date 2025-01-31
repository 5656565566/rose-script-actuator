from log import logwidget
from textual.app import ComposeResult
from textual.widgets import Footer
from textual.binding import Binding

from .page import PageScreen

class LogPage(PageScreen):
    """Textual 应用，显示日志内容"""

    BINDINGS = [
        Binding(
            "c",
            "clear_log",
            "清空日志",
            tooltip="清空日志",
        ),
        Binding(
            "ctrl+a",
            "app.maximize",
            "组件最大化",
            tooltip="组件全屏（如果页面支持）",
            show= False
        ),
    ]
    
    def action_clear_log(self):
        self.logwidget.clear()
        self.notify("日志已清空")
    
    def compose(self) -> ComposeResult:
        """布局组件"""
        
        self.logwidget = logwidget
        
        yield Footer()
        yield logwidget