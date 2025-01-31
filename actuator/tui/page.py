from rich.syntax import Syntax

from textual import work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import ScrollableContainer
from textual.screen import ModalScreen, Screen
from textual.widgets import Static

from pathlib import Path

import __main__

class CodeScreen(ModalScreen):
    DEFAULT_CSS = """
    CodeScreen {
        #code {
            border: heavy $accent;
            margin: 2 4;
            scrollbar-gutter: stable;
            Static {
                width: auto;
            }
        }
    }
    """
    BINDINGS = [("escape", "dismiss", "Dismiss code")]

    def __init__(self, title: str, code: str) -> None:
        super().__init__()
        self.code = code
        self.title = title

    def compose(self) -> ComposeResult:
        with ScrollableContainer(id="code"):
            yield Static(
                Syntax(
                    self.code, lexer="lua", indent_guides=True, line_numbers=True
                ),
                expand=True,
            )

    def on_mount(self):
        code_widget = self.query_one("#code")
        code_widget.border_title = self.title
        code_widget.border_subtitle = "按 [b]escape (Esc)[/b] 退出"


class PageScreen(Screen):
    DEFAULT_CSS = """
    PageScreen {
        width: 100%;
        height: 1fr;
        overflow-y: auto;
    }
    """
    BINDINGS = [
        Binding(
            "c",
            "show_code",
            "展示范例代码",
            tooltip="展示一个 lua 的语法范例",
        )
    ]

    @work(thread=True)
    def get_code(self, source_file: str) -> str | None:
        """Read code from disk, or return `None` on error."""
        try:
            with open(source_file, "rt", encoding="utf-8") as file_:
                return file_.read()
        except Exception:
            return None

    async def action_show_code(self):
        source_file = Path(__main__.__file__).parent / "example" / "test.lua"
        if not source_file.exists():
            self.notify(
                "无法获取示范代码 (你可能在运行单文件版本)",
                title="展示代码",
                severity="error",
            )
            return

        code = await self.get_code(source_file).wait()
        if code is None:
            self.notify(
                "无法获取示范代码 (文件被清空)",
                title="展示代码",
                severity="error",
            )
        else:
            self.app.push_screen(CodeScreen("示范代码", code))
