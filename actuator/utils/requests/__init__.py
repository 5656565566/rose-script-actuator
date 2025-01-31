import httpx
import ssl

from httpx import Response
from httpx._types import (
    CookieTypes,
    HeaderTypes,
    ProxyTypes,
    QueryParamTypes,
    RequestContent,
    RequestData,
    RequestFiles,
    TimeoutTypes,
    URLTypes,
)

from typing import Any, Literal
from dataclasses import dataclass

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from .utils import add_user_agent

@dataclass
class config:
    proxy_url  = None
    http_timeout : int = 60

class Requests:
    """
    httpx 异步请求封装
    """
    
    @staticmethod
    def set_proxy_url(url: str):
        """设置代理"""
        config.proxy_url = url
    
    @staticmethod
    def set_http_timeout(time: int):
        """设置超时时间"""
        config.http_timeout = time

    @classmethod
    async def get(
        cls,
        url: URLTypes,
        *,
        params: QueryParamTypes | None = None,
        headers: HeaderTypes | None = None,
        cookies: CookieTypes | None = None,
        follow_redirects: bool = True,
        timeout: TimeoutTypes | None = None,
        verify: ssl.SSLContext | str | bool = True,
        http2: bool = False,
        proxy: ProxyTypes | None = None,
        **kwargs,
    ) -> Response:
        """发起 GET 请求

        参数:
            url: 请求地址
            params: 请求参数
            headers: 请求头
            cookies: 请求 Cookie
            follow_redirects: 是否跟随重定向
            timeout: 尝试时间，单位：秒
            verify: 是否显示 SSL 整数
            http2: 是否使用 HTTP/2
            proxy: 代理地址
            kwargs: 传递给 `httpx.AsyncClient` 的其他参数

        返回: `httpx.Response` 对象
        """

        async with httpx.AsyncClient(
            verify=verify,
            http2=http2,
            proxy=proxy or config.proxy_url,
            **kwargs,
        ) as client:
            return await client.get(
                url,
                params=params,
                headers=add_user_agent(headers),
                cookies=cookies,
                follow_redirects=follow_redirects,
                timeout=timeout if timeout is not None else config.http_timeout,
            )
    
    @classmethod
    def get(
        cls,
        url: URLTypes,
        *,
        params: QueryParamTypes | None = None,
        headers: HeaderTypes | None = None,
        cookies: CookieTypes | None = None,
        follow_redirects: bool = True,
        timeout: TimeoutTypes | None = None,
        verify: ssl.SSLContext | str | bool = True,
        http2: bool = False,
        proxy: ProxyTypes | None = None,
        **kwargs,
    ) -> Response:
        """发起 GET 请求

        参数:
            url: 请求地址
            params: 请求参数
            headers: 请求头
            cookies: 请求 Cookie
            follow_redirects: 是否跟随重定向
            timeout: 尝试时间，单位：秒
            verify: 是否显示 SSL 整数
            http2: 是否使用 HTTP/2
            proxy: 代理地址
            kwargs: 传递给 `httpx.Client` 的其他参数

        返回: `httpx.Response` 对象
        """

        with httpx.Client(
            verify=verify,
            http2=http2,
            proxy=proxy or config.proxy_url,
            **kwargs,
        ) as client:
            return client.get(
                url,
                params=params,
                headers=add_user_agent(headers),
                cookies=cookies,
                follow_redirects=follow_redirects,
                timeout=timeout if timeout is not None else config.http_timeout,
            )

    @classmethod
    async def post(
        cls,
        url: URLTypes,
        *,
        content: RequestContent | None = None,
        data: RequestData | None = None,
        json: RequestContent | dict | None = None,
        files: RequestFiles | None = None,
        params: QueryParamTypes | None = None,
        headers: HeaderTypes | None = None,
        cookies: CookieTypes | None = None,
        follow_redirects: bool = True,
        timeout: TimeoutTypes | None = None,
        verify: ssl.SSLContext | str | bool = True,
        http2: bool = False,
        proxy: ProxyTypes | None = None,
        **kwargs,
    ) -> Response:
        """发起 POST 请求。
        
        参数:
            url: 请求地址
            content: 请求内容
            data: 请求数据
            json: 请求 JSON
            files: 请求文件
            params: 请求参数
            headers: 请求头
            cookies: 请求 Cookie
            follow_redirects: 是否跟随重定向
            timeout: 超时时间，单位: 秒
            verify: 是否验证 SSL 证书
            http2: 是否使用 HTTP/2
            proxy: 代理地址
            kwargs: 传递给 `httpx.AsyncClient` 的其他参数

        返回: `httpx.Response` 对象
        """
        async with httpx.AsyncClient(
            verify=verify,
            http2=http2,
            proxy=proxy or config.proxy_url,
            **kwargs,
        ) as client:
            return await client.post(
                url,
                content=content,
                data=data,
                files=files,
                json=json,
                params=params,
                headers=add_user_agent(headers),
                cookies=cookies,
                follow_redirects=follow_redirects,
                timeout=timeout if timeout is not None else config.http_timeout,
            )
            
    @classmethod
    def post(
        cls,
        url: URLTypes,
        *,
        content: RequestContent | None = None,
        data: RequestData | None = None,
        json: RequestContent | dict | None = None,
        files: RequestFiles | None = None,
        params: QueryParamTypes | None = None,
        headers: HeaderTypes | None = None,
        cookies: CookieTypes | None = None,
        follow_redirects: bool = True,
        timeout: TimeoutTypes | None = None,
        verify: ssl.SSLContext | str | bool = True,
        http2: bool = False,
        proxy: ProxyTypes | None = None,
        **kwargs,
    ) -> Response:
        """发起 POST 请求。
        
        参数:
            url: 请求地址
            content: 请求内容
            data: 请求数据
            json: 请求 JSON
            files: 请求文件
            params: 请求参数
            headers: 请求头
            cookies: 请求 Cookie
            follow_redirects: 是否跟随重定向
            timeout: 超时时间，单位: 秒
            verify: 是否验证 SSL 证书
            http2: 是否使用 HTTP/2
            proxy: 代理地址
            kwargs: 传递给 `httpx.Client` 的其他参数

        返回: `httpx.Response` 对象
        """
        with httpx.Client(
            verify=verify,
            http2=http2,
            proxy=proxy or config.proxy_url,
            **kwargs,
        ) as client:
            return client.post(
                url,
                content=content,
                data=data,
                files=files,
                json=json,
                params=params,
                headers=add_user_agent(headers),
                cookies=cookies,
                follow_redirects=follow_redirects,
                timeout=timeout if timeout is not None else config.http_timeout,
            )

    @classmethod
    async def put(
        cls,
        url: URLTypes,
        *,
        content: RequestContent | None = None,
        data: RequestData | None = None,
        files: RequestFiles | None = None,
        json: Any = None,
        params: QueryParamTypes | None = None,
        headers: HeaderTypes | None = None,
        cookies: CookieTypes | None = None,
        follow_redirects: bool = True,
        timeout: TimeoutTypes | None = None,
        verify: ssl.SSLContext | str | bool = True,
        http2: bool = False,
        proxy: ProxyTypes | None = None,
        **kwargs,
    ) -> Response:
        """发起 PUT 请求。

        参数:
            url: 请求地址
            content: 请求内容
            data: 请求数据
            files: 请求文件
            json: 请求 JSON
            params: 请求参数
            headers: 请求头
            cookies: 请求 Cookie
            follow_redirects: 是否跟随重定向
            timeout: 超时时间，单位: 秒
            verify: 是否验证 SSL 证书
            http2: 是否使用 HTTP/2
            proxy: 代理地址
            :kwargs: 传递给 `httpx.AsyncClient` 的其他参数

        返回:  `httpx.Response` 对象
        """
        async with httpx.AsyncClient(
            verify=verify,
            http2=http2,
            proxy=proxy or config.proxy_url,
            **kwargs,
        ) as client:
            return await client.put(
                url,
                content=content,
                data=data,
                files=files,
                json=json,
                params=params,
                headers=add_user_agent(headers),
                cookies=cookies,
                follow_redirects=follow_redirects,
                timeout=timeout if timeout is not None else config.http_timeout,
            )
            
    @classmethod
    def put(
        cls,
        url: URLTypes,
        *,
        content: RequestContent | None = None,
        data: RequestData | None = None,
        files: RequestFiles | None = None,
        json: Any = None,
        params: QueryParamTypes | None = None,
        headers: HeaderTypes | None = None,
        cookies: CookieTypes | None = None,
        follow_redirects: bool = True,
        timeout: TimeoutTypes | None = None,
        verify: ssl.SSLContext | str | bool = True,
        http2: bool = False,
        proxy: ProxyTypes | None = None,
        **kwargs,
    ) -> Response:
        """发起 PUT 请求。

        参数:
            url: 请求地址
            content: 请求内容
            data: 请求数据
            files: 请求文件
            json: 请求 JSON
            params: 请求参数
            headers: 请求头
            cookies: 请求 Cookie
            follow_redirects: 是否跟随重定向
            timeout: 超时时间，单位: 秒
            verify: 是否验证 SSL 证书
            http2: 是否使用 HTTP/2
            proxy: 代理地址
            :kwargs: 传递给 `httpx.AsyncClient` 的其他参数

        返回:  `httpx.Response` 对象
        """
        with httpx.Client(
            verify=verify,
            http2=http2,
            proxy=proxy or config.proxy_url,
            **kwargs,
        ) as client:
            return client.put(
                url,
                content=content,
                data=data,
                files=files,
                json=json,
                params=params,
                headers=add_user_agent(headers),
                cookies=cookies,
                follow_redirects=follow_redirects,
                timeout=timeout if timeout is not None else config.http_timeout,
            )

    @classmethod
    async def delete(
        cls,
        url: URLTypes,
        *,
        params: QueryParamTypes | None = None,
        headers: HeaderTypes | None = None,
        cookies: CookieTypes | None = None,
        follow_redirects: bool = True,
        timeout: TimeoutTypes | None = None,
        verify: ssl.SSLContext | str | bool = True,
        http2: bool = False,
        proxy: ProxyTypes | None = None,
        **kwargs,
    ) -> Response:
        """发起 DELETE 请求。

        参数:
            url: 请求地址
            params: 请求参数
            headers: 请求头
            cookies: 请求 Cookie
            follow_redirects: 是否跟随重定向
            timeout: 超时时间，单位: 秒
            verify: 是否验证 SSL 证书
            http2: 是否使用 HTTP/2
            proxy: 代理地址
            kwargs: 传递给 `httpx.AsyncClient` 的其他参数

        返回:  `httpx.Response` 对象
        """
        async with httpx.AsyncClient(
            verify=verify,
            http2=http2,
            proxy=proxy or config.proxy_url,
            **kwargs,
        ) as client:
            return await client.delete(
                url,
                params=params,
                headers=add_user_agent(headers),
                cookies=cookies,
                follow_redirects=follow_redirects,
                timeout=timeout if timeout is not None else config.http_timeout,
            )
            
    @classmethod
    def delete(
        cls,
        url: URLTypes,
        *,
        params: QueryParamTypes | None = None,
        headers: HeaderTypes | None = None,
        cookies: CookieTypes | None = None,
        follow_redirects: bool = True,
        timeout: TimeoutTypes | None = None,
        verify: ssl.SSLContext | str | bool = True,
        http2: bool = False,
        proxy: ProxyTypes | None = None,
        **kwargs,
    ) -> Response:
        """发起 DELETE 请求。

        参数:
            url: 请求地址
            params: 请求参数
            headers: 请求头
            cookies: 请求 Cookie
            follow_redirects: 是否跟随重定向
            timeout: 超时时间，单位: 秒
            verify: 是否验证 SSL 证书
            http2: 是否使用 HTTP/2
            proxy: 代理地址
            kwargs: 传递给 `httpx.Client` 的其他参数

        返回:  `httpx.Response` 对象
        """
        with httpx.Client(
            verify=verify,
            http2=http2,
            proxy=proxy or config.proxy_url,
            **kwargs,
        ) as client:
            return client.delete(
                url,
                params=params,
                headers=add_user_agent(headers),
                cookies=cookies,
                follow_redirects=follow_redirects,
                timeout=timeout if timeout is not None else config.http_timeout,
            )

    @classmethod
    async def patch(
        cls,
        url: URLTypes,
        *,
        content: RequestContent | None = None,
        data: RequestData | None = None,
        files: RequestFiles | None = None,
        json: Any = None,
        params: QueryParamTypes | None = None,
        headers: HeaderTypes | None = None,
        cookies: CookieTypes | None = None,
        follow_redirects: bool = True,
        timeout: TimeoutTypes | None = None,
        verify: ssl.SSLContext | str | bool = True,
        http2: bool = False,
        proxy: ProxyTypes | None = None,
        **kwargs,
    ) -> Response:
        """发起 PATCH 请求。

        参数:
            url: 请求地址
            content: 请求内容
            data: 请求数据
            files: 请求文件
            json: 请求 JSON
            params: 请求参数
            headers: 请求头
            cookies: 请求 Cookie
            follow_redirects: 是否跟随重定向
            timeout: 超时时间，单位: 秒
            verify: 是否验证 SSL 证书
            http2: 是否使用 HTTP/2
            proxy: 代理地址
            kwargs: 传递给 `httpx.AsyncClient` 的其他参数

        返回:  `httpx.Response` 对象
        """
        async with httpx.AsyncClient(
            verify=verify,
            http2=http2,
            proxy=proxy or config.proxy_url,
            **kwargs,
        ) as client:
            return await client.patch(
                url,
                content=content,
                data=data,
                files=files,
                json=json,
                params=params,
                headers=add_user_agent(headers),
                cookies=cookies,
                follow_redirects=follow_redirects,
                timeout=timeout if timeout is not None else config.http_timeout,
            )
            
    @classmethod
    def patch(
        cls,
        url: URLTypes,
        *,
        content: RequestContent | None = None,
        data: RequestData | None = None,
        files: RequestFiles | None = None,
        json: Any = None,
        params: QueryParamTypes | None = None,
        headers: HeaderTypes | None = None,
        cookies: CookieTypes | None = None,
        follow_redirects: bool = True,
        timeout: TimeoutTypes | None = None,
        verify: ssl.SSLContext | str | bool = True,
        http2: bool = False,
        proxy: ProxyTypes | None = None,
        **kwargs,
    ) -> Response:
        """发起 PATCH 请求。

        参数:
            url: 请求地址
            content: 请求内容
            data: 请求数据
            files: 请求文件
            json: 请求 JSON
            params: 请求参数
            headers: 请求头
            cookies: 请求 Cookie
            follow_redirects: 是否跟随重定向
            timeout: 超时时间，单位: 秒
            verify: 是否验证 SSL 证书
            http2: 是否使用 HTTP/2
            proxy: 代理地址
            kwargs: 传递给 `httpx.Client` 的其他参数

        返回:  `httpx.Response` 对象
        """
        with httpx.Client(
            verify=verify,
            http2=http2,
            proxy=proxy or config.proxy_url,
            **kwargs,
        ) as client:
            return client.patch(
                url,
                content=content,
                data=data,
                files=files,
                json=json,
                params=params,
                headers=add_user_agent(headers),
                cookies=cookies,
                follow_redirects=follow_redirects,
                timeout=timeout if timeout is not None else config.http_timeout,
            )

    @classmethod
    async def head(
        cls,
        url: URLTypes,
        *,
        params: QueryParamTypes | None = None,
        headers: HeaderTypes | None = None,
        cookies: CookieTypes | None = None,
        follow_redirects: bool = True,
        timeout: TimeoutTypes | None = None,
        verify: ssl.SSLContext | str | bool = True,
        http2: bool = False,
        proxy: ProxyTypes | None = None,
        **kwargs,
    ) -> Response:
        """发起 HEAD 请求。

        参数:
            url: 请求地址
            params: 请求参数
            headers: 请求头
            cookies: 请求 Cookie
            follow_redirects: 是否跟随重定向
            timeout: 超时时间，单位: 秒
            verify: 是否验证 SSL 证书
            http2: 是否使用 HTTP/2
            proxy: 代理地址
            kwargs: 传递给 `httpx.AsyncClient` 的其他参数

        返回:  `httpx.Response` 对象
        """
        async with httpx.AsyncClient(
            verify=verify,
            http2=http2,
            proxy=proxy or config.proxy_url,
            **kwargs,
        ) as client:
            return await client.head(
                url,
                params=params,
                headers=add_user_agent(headers),
                cookies=cookies,
                follow_redirects=follow_redirects,
                timeout=timeout if timeout is not None else config.http_timeout,
            )
            
    @classmethod
    def head(
        cls,
        url: URLTypes,
        *,
        params: QueryParamTypes | None = None,
        headers: HeaderTypes | None = None,
        cookies: CookieTypes | None = None,
        follow_redirects: bool = True,
        timeout: TimeoutTypes | None = None,
        verify: ssl.SSLContext | str | bool = True,
        http2: bool = False,
        proxy: ProxyTypes | None = None,
        **kwargs,
    ) -> Response:
        """发起 HEAD 请求。

        参数:
            url: 请求地址
            params: 请求参数
            headers: 请求头
            cookies: 请求 Cookie
            follow_redirects: 是否跟随重定向
            timeout: 超时时间，单位: 秒
            verify: 是否验证 SSL 证书
            http2: 是否使用 HTTP/2
            proxy: 代理地址
            kwargs: 传递给 `httpx.Client` 的其他参数

        返回:  `httpx.Response` 对象
        """
        with httpx.Client(
            verify=verify,
            http2=http2,
            proxy=proxy or config.proxy_url,
            **kwargs,
        ) as client:
            return client.head(
                url,
                params=params,
                headers=add_user_agent(headers),
                cookies=cookies,
                follow_redirects=follow_redirects,
                timeout=timeout if timeout is not None else config.http_timeout,
            )

    @classmethod
    async def options(
        cls,
        url: URLTypes,
        *,
        params: QueryParamTypes | None = None,
        headers: HeaderTypes | None = None,
        cookies: CookieTypes | None = None,
        follow_redirects: bool = True,
        timeout: TimeoutTypes | None = None,
        verify: ssl.SSLContext | str | bool = True,
        http2: bool = False,
        proxy: ProxyTypes | None = None,
        **kwargs,
    ) -> Response:
        """发起 OPTIONS 请求。

        参数:
            url: 请求地址
            params: 请求参数
            headers: 请求头
            cookies: 请求 Cookie
            follow_redirects: 是否跟随重定向
            timeout: 超时时间，单位: 秒
            verify: 是否验证 SSL 证书
            http2: 是否使用 HTTP/2
            proxy: 代理地址
            kwargs: 传递给 `httpx.AsyncClient` 的其他参数

        返回:  `httpx.Response` 对象
        """
        async with httpx.AsyncClient(
            verify=verify,
            http2=http2,
            proxy=proxy or config.proxy_url,
            **kwargs,
        ) as client:
            return await client.options(
                url,
                params=params,
                headers=add_user_agent(headers),
                cookies=cookies,
                follow_redirects=follow_redirects,
                timeout=timeout if timeout is not None else config.http_timeout,
            )
    
    @classmethod
    def options(
        cls,
        url: URLTypes,
        *,
        params: QueryParamTypes | None = None,
        headers: HeaderTypes | None = None,
        cookies: CookieTypes | None = None,
        follow_redirects: bool = True,
        timeout: TimeoutTypes | None = None,
        verify: ssl.SSLContext | str | bool = True,
        http2: bool = False,
        proxy: ProxyTypes | None = None,
        **kwargs,
    ) -> Response:
        """发起 OPTIONS 请求。

        参数:
            url: 请求地址
            params: 请求参数
            headers: 请求头
            cookies: 请求 Cookie
            follow_redirects: 是否跟随重定向
            timeout: 超时时间，单位: 秒
            verify: 是否验证 SSL 证书
            http2: 是否使用 HTTP/2
            proxy: 代理地址
            kwargs: 传递给 `httpx.Client` 的其他参数

        返回:  `httpx.Response` 对象
        """
        with httpx.Client(
            verify=verify,
            http2=http2,
            proxy=proxy or config.proxy_url,
            **kwargs,
        ) as client:
            return client.options(
                url,
                params=params,
                headers=add_user_agent(headers),
                cookies=cookies,
                follow_redirects=follow_redirects,
                timeout=timeout if timeout is not None else config.http_timeout,
            )

    @classmethod
    async def request(
        cls,
        method: Literal["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"],
        url: URLTypes,
        *,
        content: RequestContent | None = None,
        data: RequestData | None = None,
        files: RequestFiles | None = None,
        json: Any = None,
        params: QueryParamTypes | None = None,
        headers: HeaderTypes | None = None,
        cookies: CookieTypes | None = None,
        follow_redirects: bool = True,
        timeout: TimeoutTypes | None = None,
        verify: ssl.SSLContext | str | bool = True,
        http2: bool = False,
        proxy: ProxyTypes | None = None,
        **kwargs,
    ) -> Response:
        """发起请求。

        参数:
            method: 请求方法
            url: 请求地址
            content: 请求内容
            data: 请求数据
            files: 请求文件
            json: 请求 JSON
            params: 请求参数
            headers: 请求头
            cookies: 请求 Cookie
            follow_redirects: 是否跟随重定向
            timeout: 超时时间，单位: 秒
            verify: 是否验证 SSL 证书
            http2: 是否使用 HTTP/2
            proxy: 代理地址
            kwargs: 传递给 `httpx.AsyncClient` 的其他参数

        返回:  `httpx.Response` 对象
        """
        async with httpx.AsyncClient(
            verify=verify,
            http2=http2,
            proxy=proxy or config.proxy_url,
            **kwargs,
        ) as client:
            return await client.request(
                method,
                url,
                content=content,
                data=data,
                files=files,
                json=json,
                params=params,
                headers=add_user_agent(headers),
                cookies=cookies,
                follow_redirects=follow_redirects,
                timeout=timeout if timeout is not None else config.http_timeout,
            )
            
    @classmethod
    def request(
        cls,
        method: Literal["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"],
        url: URLTypes,
        *,
        content: RequestContent | None = None,
        data: RequestData | None = None,
        files: RequestFiles | None = None,
        json: Any = None,
        params: QueryParamTypes | None = None,
        headers: HeaderTypes | None = None,
        cookies: CookieTypes | None = None,
        follow_redirects: bool = True,
        timeout: TimeoutTypes | None = None,
        verify: ssl.SSLContext | str | bool = True,
        http2: bool = False,
        proxy: ProxyTypes | None = None,
        **kwargs,
    ) -> Response:
        """发起请求。

        参数:
            method: 请求方法
            url: 请求地址
            content: 请求内容
            data: 请求数据
            files: 请求文件
            json: 请求 JSON
            params: 请求参数
            headers: 请求头
            cookies: 请求 Cookie
            follow_redirects: 是否跟随重定向
            timeout: 超时时间，单位: 秒
            verify: 是否验证 SSL 证书
            http2: 是否使用 HTTP/2
            proxy: 代理地址
            kwargs: 传递给 `httpx.AsyncClient` 的其他参数

        返回:  `httpx.Response` 对象
        """
        with httpx.Client(
            verify=verify,
            http2=http2,
            proxy=proxy or config.proxy_url,
            **kwargs,
        ) as client:
            return client.request(
                method,
                url,
                content=content,
                data=data,
                files=files,
                json=json,
                params=params,
                headers=add_user_agent(headers),
                cookies=cookies,
                follow_redirects=follow_redirects,
                timeout=timeout if timeout is not None else config.http_timeout,
            )

    @classmethod
    @asynccontextmanager
    async def stream(
        cls,
        method: Literal["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"],
        url: URLTypes,
        *,
        content: RequestContent | None = None,
        data: RequestData | None = None,
        files: RequestFiles | None = None,
        json: Any = None,
        params: QueryParamTypes | None = None,
        headers: HeaderTypes | None = None,
        cookies: CookieTypes | None = None,
        follow_redirects: bool = True,
        timeout: TimeoutTypes | None = None,
        verify: ssl.SSLContext | str | bool = True,
        http2: bool = False,
        proxy: ProxyTypes | None = None,
        **kwargs,
    ) -> AsyncGenerator[Response, None]:
        """发起流式请求。

        参数:
            method: 请求方法
            url: 请求地址
            content: 请求内容
            data: 请求数据
            files: 请求文件
            json: 请求 JSON
            params: 请求参数
            headers: 请求头
            cookies: 请求 Cookie
            follow_redirects: 是否跟随重定向
            timeout: 超时时间，单位: 秒
            verify: 是否验证 SSL 证书
            http2: 是否使用 HTTP/2
            proxy: 代理地址
            kwargs: 传递给 `httpx.AsyncClient` 的其他参数

        返回:  `httpx.Response` 对象
        """
        async with httpx.AsyncClient(
            verify=verify,
            http2=http2,
            proxy=proxy or config.proxy_url,
            **kwargs,
        ) as client, client.stream(
            method,
            url,
            content=content,
            data=data,
            files=files,
            json=json,
            params=params,
            headers=add_user_agent(headers),
            cookies=cookies,
            follow_redirects=follow_redirects,
            timeout=timeout if timeout is not None else config.http_timeout,
        ) as response:
            yield response

    @classmethod
    @asynccontextmanager
    async def client_session(
        cls,
        verify: ssl.SSLContext | str | bool = True,
        http2: bool = False,
        proxy: ProxyTypes | None = None,
        follow_redirects: bool = True,
        **kwargs,
    ) -> AsyncGenerator[httpx.AsyncClient, None]:
        """创建 `httpx.AsyncClient` 会话。

        参数:
            verify: 是否验证 SSL 证书
            http2: 是否使用 HTTP/2
            proxies: 地址
            follow_redirects: 是否跟随重定向
            kwargs: 传递给 `httpx.AsyncClient` 的其他参数

        返回:  `httpx.AsyncClient` 对象
        """
        async with httpx.AsyncClient(
            verify=verify,
            http2=http2,
            proxy=proxy or config.proxy_url,
            follow_redirects=follow_redirects,
            **kwargs,
        ) as client:
            yield client