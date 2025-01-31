## 网络请求
```lua
-- 设置代理
Requests.set_proxy_url("http://xxx")

-- 设置超时时间（秒）
Requests.set_timeout(60)

-- * 后为可选
-- Get 请求
response = Requests.get(url, *, content, data, files, json, params, headers, cookies, follow_redirects, timeout, verify, http2, proxy)

-- Post 请求
response = Requests.post(url, *, content, data, files, json, params, headers, cookies, follow_redirects, timeout, verify, http2, proxy)

-- Put 请求
response = Requests.put(url, *, content, data, files, json, params, headers, cookies, follow_redirects, timeout, verify, http2, proxy)

-- Delete 请求
response = Requests.delete(url, *, params, headers, cookies, follow_redirects, timeout, verify, http2, proxy)

-- Patch 请求
response = Requests.patch(url, *, content, data, files, json, params, headers, cookies, follow_redirects, timeout, verify, http2, proxy)

-- Head 请求
response = Requests.head(url, *, params, headers, cookies, follow_redirects, timeout, verify, http2, proxy)

-- Options 请求
response = Requests.options(url, *, params, headers, cookies, follow_redirects, timeout, verify, http2, proxy)

-- 发起请求
method = "GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"
Requests.request(method, url, *, content, data, files, json, params, headers, cookies, follow_redirects, timeout, verify, http2, proxy)
```

## 请求后获取到 Response 对象
```lua
-- 获取响应状态码
status_code = response.status_code

-- 获取响应头（以表的形式返回）
headers = response.headers

-- 获取响应内容（文本格式）
text = response.text

-- 获取响应内容（二进制格式）
content = response.content

-- 获取响应内容（JSON 格式）
json_data = response.json()

-- 获取响应内容的编码
encoding = response.encoding

-- 获取响应的 URL（可能包含重定向后的 URL）
url = response.url

-- 获取响应的历史记录（如果有重定向）
history = response.history

-- 获取响应的 cookies
cookies = response.cookies

-- 检查请求是否成功（状态码为 2xx）
is_success = response.is_success

-- 检查请求是否重定向
is_redirect = response.is_redirect

-- 检查请求是否客户端错误（状态码为 4xx）
is_client_error = response.is_client_error

-- 检查请求是否服务器错误（状态码为 5xx）
is_server_error = response.is_server_error

-- 获取响应的原始字节流
raw = response.raw

-- 获取响应的请求对象（包含请求的详细信息）
request = response.request

-- 获取响应的耗时（秒）
elapsed_time = response.elapsed.total_seconds()

-- 获取响应的 HTTP 版本（如 "HTTP/1.1" 或 "HTTP/2"）
http_version = response.http_version

-- 获取响应的重定向次数
redirect_count = len(response.history)

-- 获取响应的最终 URL（如果有重定向）
final_url = response.url

```