import secrets

from typing import Literal
from collections.abc import Sequence

from httpx._types import HeaderTypes
from .user_agent import data

def fake_user_agent(
    browser: Literal["chrome", "opera", "firefox", "safari", "internetexplorer"]
    | None = None,
) -> dict[str, str]:
    """
    获取一个随机的 User-Agent
    browser 浏览器类型，如果不指定则随机选择
    """

    if not browser:
        browser = secrets.choice(list(data["randomize"].values()))
    return {"User-Agent": secrets.choice(data["browsers"][browser])}


def add_user_agent(headers: HeaderTypes | None = None) -> HeaderTypes:
    """
    添加随机的 User-Agent 到请求头中
    headers 请求头字典或列表
    return 添加了随机 User-Agent 的请求头字典
    """
    user_agent = fake_user_agent()
    if headers:
        _headers = dict(headers) if isinstance(headers, Sequence) else headers
        return {**user_agent, **_headers}
    return user_agent