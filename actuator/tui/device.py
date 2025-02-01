from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import ScrollableContainer
from textual.screen import Screen
from textual.widgets import Button, Static, Footer, Markdown
from textual import work

from typing import Type

from consts import devices_manager
from base import Devices

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
                        device.name,
                        classes="file-btn",
                        action=f"screen.device_test({device.name!r})",
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
                                device.name,
                                classes="file-btn",
                                action=f"screen.device_test({device.name!r})",
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

    @work(thread= True)
    def device_test(self, device: str):
        devices_manager.select_devices(device)
        result = devices_manager.device.screenshot(filePath= f"{device}.png")
        if len(result) == 2:
            self.app.call_from_thread(self.notify, f"设备 {device} 截图失败", severity="error")
        else:
            self.app.call_from_thread(self.notify, f"设备 {device} 截图成功 保存到 {device}.png!")
    
    def action_device_test(self, device: str):
        self.notify(f"尝试为设备 {device} 截图 !")
        self.device_test(device)
    
    @staticmethod
    def get_devices() -> dict[str, list[Type[Devices]]]:
        devices_manager.init_platforms()
        return devices_manager.get_devices()
