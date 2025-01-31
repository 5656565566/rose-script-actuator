from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import ScrollableContainer
from textual.screen import Screen
from textual.widgets import Button, Static, Footer, Markdown


class DevicesScreen(Screen):
    DEFAULT_CSS = """
    DevicesScreen {
        width: 100%;
        height: 1fr;
        overflow-y: auto;
    }

    DevicesScreen > #file-list {
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
            "r",
            "get_script_list",
            "刷新",
            tooltip="刷新设备列表",
        ),
    ]

    def __init__(self, name=None, id=None, classes=None):
        self.devices = self.get_devices()
        self.script_message: str = ""
        
        super().__init__(name, id, classes)
        
    
    def compose(self) -> ComposeResult:
        """动态生成文件列表界面"""

        yield Footer()
        yield Markdown("# 设备列表\n## 单击设备对设备截图 (并非所有设备生效)")

        if not self.devices:
            yield Static("[red]未连接任何设备 ![/red] 使用 [b]H[/b] 返回主页", classes="error")
            return

        with ScrollableContainer(id="file-list", can_maximize=True):
            for devices in self.devices.keys():
                yield Markdown(f"### {devices}")
                for device in self.devices[devices]:
                    yield Button(
                        device,
                        classes="file-btn",
                        action=f"screen.run_script({str(device)!r})",
                    )
                if len(self.devices[devices]) == 0:
                    yield Button(
                        "此项目无设备",
                        classes="file-btn",
                    )
    
    def action_get_script_list(self) -> None:
        """获取并刷新当前目录下的Lua脚本列表"""
        try:
            self.devices = self.get_devices()
            
            self.refresh()

            list_container = self.query_one("#file-list")
            
            list_container.remove_children()
            if self.devices:
                for devices in self.devices.keys():
                    list_container.mount(Markdown(f"### {devices}"))
                    for device in self.devices[devices]:
                        list_container.mount(
                            Button(
                                device,
                                classes="file-btn",
                                action=f"screen.run_script({str(device)!r})",
                            )
                        )
                    if len(self.devices[devices]) == 0:
                        list_container.mount(
                            Button(
                                "此项目无设备",
                                classes="file-btn",
                            )
                        )
                
            list_container.refresh(layout=True)
            self.notify("成功刷新了设备列表")
            
        except Exception as e:
            self.notify(
                f"未知错误：{str(e)}", 
                title="刷新失败", 
                severity="error"
            )
            return None

    @staticmethod
    def get_devices() -> dict[str, str]:
        
        return {"Windows\n在 Windows 环境下运行可启用" : ["本机"], "Android\n通过 USB 连接设备 或 配置文件配置通过网络的 adb 设备 添加" : [], "浏览器\n通过在当前目录放置 msedgedriver.exe 等浏览器驱动添加": []}
