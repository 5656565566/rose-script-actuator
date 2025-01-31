import inspect
import logging
import loguru

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from loguru import Logger, Record


logger: "Logger" = loguru.logger
"""日志记录器对象。

默认信息:

- 格式: `[%(asctime)s %(name)s] %(levelname)s: %(message)s`
- 等级: `INFO` ，根据 `config.log_level` 配置改变
- 输出: 输出至 stdout

"""

log_level = "INFO"

class LoguruHandler(logging.Handler):  # pragma: no cover
    """logging 与 loguru 之间的桥梁，将 logging 的日志转发到 loguru。"""

    def emit(self, record: logging.LogRecord):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = inspect.currentframe(), 0
        while frame and (depth == 0 or frame.f_code.co_filename == logging.__file__):
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def default_filter(record: "Record"):    
    """默认的日志过滤器，根据 `config.log_level` 配置改变日志等级。"""
    levelno = logger.level(log_level).no if isinstance(log_level, str) else log_level
    return record["level"].no >= levelno


def set_log_level(level: str):
    global log_level
    log_level = level

default_format: str = (
    "<g>{time:MM-DD HH:mm:ss}</g> "
    "[<lvl>{level}</lvl>] "
    # "<c><u>{name}</u></c> | "
    # "<c>{function}:{line}</c>| "
    "{message}"
)

from textual.widgets import RichLog

class LogWidget(RichLog):
    """用于显示日志内容的 Textual 组件"""

    def __init__(self):
        super().__init__(wrap=True, highlight=True, markup=True)

    def add_log(self, log: str):
        """添加日志内容"""
        self.write(log)

class LogSink:
    """自定义 Loguru Sink，将日志发送到 Textual 页面"""

    def __init__(self, log_widget: LogWidget):
        self.log_widget = log_widget

    def write(self, message):
        """将日志内容发送到 Textual 页面"""
        self.log_widget.add_log(message)

    def flush(self):
        pass

logwidget = LogWidget()

logger.remove()
logger_id = logger.add(
    LogSink(logwidget),
    level=0,
    diagnose=False,
    filter=default_filter,
    format=default_format,
)

logger.info("程序成功开启 !")