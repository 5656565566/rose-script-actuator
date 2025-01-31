## 基础函数
```lua
-- 打印消息到控制台
print("message")                  -- 输出：message
-- 延迟
sleep(1.5)                        -- 等待1.5秒
-- 发送通知
notify("message")                 -- 显示通知 "message"
-- 断言条件为真，否则抛出错误
assert(1+1 == 2, "Math error")    -- 条件成立时无输出
-- 手动触发垃圾回收
collectgarbage("collect")         -- 执行完整垃圾回收周期
-- 执行指定Lua文件
dofile("test.lua")                -- 加载并运行test.lua
-- 抛出错误对象
error("critical error", 2)        -- 抛出带层级信息的错误
-- 获取表的元表
getmetatable({})                  -- 返回nil（空表无元表）
-- 迭代数组部分
for i,v in ipairs({"a","b"}) do print(i,v) end  -- 输出：1 a  2 b
-- 加载代码块
load("print('hi')")()            -- 输出：hi
-- 加载文件代码块
loadfile("lib.lua")              -- 返回加载的函数
-- 获取表的下一个键值对
next({a=1}, nil)                 -- 返回第一个键值对：'a'和1
-- 迭代全表键值对
for k,v in pairs({x=10}) do print(k,v) end  -- 输出：x 10
-- 保护模式调用函数
pcall(function() error("test") end) -- 返回false和错误信息
-- 原始值比较
rawequal(1, 1.0)                 -- 返回false（类型不同）
-- 绕过元方法获取表值
rawget({__index=5}, "key")       -- 返回nil
-- 获取对象的原始长度
rawlen("abcd")                   -- 返回4（字符串长度）
-- 绕过元方法设置表值
rawset({}, "key", 100)           -- 返回{key=100}
-- 加载模块
require("math")                  -- 返回math模块
-- 选择参数子集
select(2, "a","b","c")           -- 返回"b","c"
-- 设置表的元表
setmetatable({}, {__tostring=function() return "obj" end})
-- 转换为数字
tonumber("FF", 16)               -- 返回255
-- 转换为字符串
tostring({})                     -- 返回"table: 0x..."
-- 检测变量类型
type(nil)                        -- 返回"nil"
-- 输出警告信息
warn("deprecated API")           -- [标准错误输出显示警告]
-- 带错误处理的保护调用
xpcall(function() error() end, debug.traceback) -- 返回false和堆栈
```

## 协程库
```lua
-- 关闭挂起的协程并释放资源
coroutine.close(coroutine.create(function() end))  -- 关闭新建的未运行协程
-- 创建新协程（返回thread对象）
local co = coroutine.create(function() print("hi") end)
-- 检查当前能否让出协程
coroutine.isyieldable()                            -- 主线程返回false
-- 启动/继续协程执行
coroutine.resume(co)                               -- 输出：hi
-- 获取当前运行的协程
coroutine.running()                                -- 返回当前协程对象
-- 查看协程状态
coroutine.status(co)                               -- 返回"dead"
-- 创建返回函数的协程包装器
local f = coroutine.wrap(function() return 1 end)
print(f())                                         -- 输出：1
-- 让出协程执行权
coroutine.yield("data")                            -- 向resume的调用方返回"data"
```

## 字符串库
```lua
-- 获取字符的ASCII码
string.byte("ABC", 2)                              -- 返回66
-- 将ASCII码转为字符
string.char(65, 66)                                -- 返回"AB"
-- 序列化函数为二进制
string.dump(print)                                 -- 返回包含字节码的字符串
-- 查找子串位置
string.find("hello", "ll")                         -- 返回3,4
-- 格式化字符串
string.format("PI:%.2f", math.pi)                  -- 返回"PI:3.14"
-- 全局模式匹配迭代器
for w in string.gmatch("a=1,b=2", "%d+") do print(w) end  -- 输出1和2
-- 全局替换子串
string.gsub("Lua","L","l")                         -- 返回"lua"和替换次数1
-- 获取字符串长度
string.len("汉字")                                  -- UTF-8返回6字节长度
-- 转为小写
string.lower("Hello")                              -- 返回"hello"
-- 模式匹配提取
string.match("ID:123", "%d+")                      -- 返回"123"
-- 按格式打包数据
string.pack("ii", 10, 20)                          -- 返回8字节二进制数据
-- 获取打包格式长度
string.packsize("i")                               -- 返回4
-- 重复字符串
string.rep("ab",3)                                 -- 返回"ababab"
-- 反转字符串
string.reverse("Lua")                              -- 返回"auL"
-- 截取子串
string.sub("ABCDE",2,4)                            -- 返回"BCD"
-- 解包二进制数据
string.unpack("ii", "\\10\\0\\0\\0\\20\\0\\0\\0")          -- 返回10,20和偏移量9
-- 转为大写
string.upper("test")                               -- 返回"TEST"
```

## 表库
```lua
-- 连接数组元素
table.concat({"A","B"}, "-")                       -- 返回"A-B"
-- 插入元素
table.insert({1,3}, 2, 2)                          -- 变为{1,2,3}
-- 移动元素块
table.move({5,6,7},1,2,3,{})                       -- 返回{5,6,5,6}
-- 打包参数为表
table.pack(1,nil,3)                                -- 返回{[1]=1, [2]=nil, [3]=3, n=3}
-- 删除元素
table.remove({"a","b"},1)                          -- 返回"a"，表变{"b"}
-- 排序表元素
table.sort({3,1,2})                                -- 排序后为{1,2,3}
-- 展开表为多返回值
table.unpack({10,20,30})                           -- 返回10,20,30
```

## 数学库
```lua
-- 绝对值
math.abs(-5.2)                                     -- 返回5.2
-- 反余弦（弧度）
math.acos(0.5)                                     -- 返回1.0471975511966
-- 反正弦（弧度）
math.asin(0.5)                                     -- 返回0.5235987755983
-- 反正切（弧度）
math.atan(1)                                       -- 返回0.78539816339745
-- 向上取整
math.ceil(3.2)                                     -- 返回4
-- 余弦值
math.cos(math.pi/3)                                -- 返回0.5
-- 弧度转角度
math.deg(math.pi)                                  -- 返回180
-- 指数运算
math.exp(1)                                        -- 返回2.718281828459
-- 向下取整
math.floor(3.8)                                    -- 返回3
-- 取模运算
math.fmod(10.5,3)                                  -- 返回1.5
-- 对数运算
math.log(100,10)                                   -- 返回2
-- 取最大值
math.max(5,9,3)                                    -- 返回9
-- 取最小值
math.min(5,9,3)                                    -- 返回3
-- 分离整数和小数
math.modf(3.14)                                    -- 返回3,0.14
-- 角度转弧度
math.rad(180)                                      -- 返回3.1415926535898
-- 生成随机数
math.random(1,100)                                 -- 返回1-100间的整数
-- 设置随机种子
math.randomseed(os.time())
-- 正弦值
math.sin(math.pi/6)                                -- 返回0.5
-- 平方根
math.sqrt(25)                                      -- 返回5
-- 正切值
math.tan(math.pi/4)                                -- 返回1.0
-- 转换为整型数
math.tointeger(3.0)                                -- 返回3
-- 数值类型检测
math.type(3)                                       -- 返回"integer"
-- 无符号整型比较
math.ult(-1, 1)                                    -- 返回true（按无符号比较）
-- 圆周率（常量）
math.pi                                            -- 约3.1415926535898
-- 无穷大（常量）
math.huge                                          -- 表示inf
-- 最大整型数（常量）
math.maxinteger                                    -- 如9223372036854775807
-- 最小整型数（常量）
math.mininteger                                    -- 如-9223372036854775808
```

## 文件操作库
```lua
-- 关闭文件句柄
local f = io.open("test.txt"); io.close(f)
-- 强制写入缓冲数据
io.flush()                                         -- 立即输出缓存内容
-- 设置默认输入文件
io.input("input.txt")                              -- 后续读操作来自该文件
-- 迭代文件行
for line in io.lines("data.txt") do print(line) end
-- 打开文件
local f = io.open("test.txt", "r")                 -- 以只读模式打开
-- 设置默认输出文件
io.output("log.txt")                               -- 后续写操作输出到该文件
-- 创建管道进程
local p = io.popen("ls", "r")                      -- 执行ls命令
-- 读取内容
io.read("*all")                                    -- 读取全部内容
-- 标准错误输出（常量）
io.stderr:write("Error!")                          -- 输出到标准错误
-- 标准输入（常量）
local input = io.stdin:read()                      -- 读取用户输入
-- 标准输出（常量）
io.stdout:write("Hello")                           -- 输出到控制台
-- 创建临时文件
local tmp = io.tmpfile()                           -- 返回临时文件句柄
-- 检测对象类型
io.type(f)                                         -- 返回"file"
-- 写入内容
io.write("text")                                   -- 输出到当前输出流
```

## 操作系统库
```lua
-- 获取程序CPU时间
os.clock()                                         -- 返回使用的CPU秒数
-- 格式化时间
os.date("%Y-%m-%d")                                -- 返回"2023-08-10"
-- 计算时间差
os.difftime(os.time(), start_time)                 -- 返回秒数差值
-- 执行系统命令
os.execute("mkdir folder")                         -- 创建目录
-- 退出程序
os.exit("原因")                                     -- 立即退出并且提示用户原因
-- 获取环境变量
os.getenv("PATH")                                  -- 返回PATH变量值
-- 删除文件
os.remove("temp.txt")                              -- 删除指定文件
-- 重命名文件
os.rename("old.txt","new.txt")                     -- 修改文件名
-- 设置区域设置
os.setlocale("en_US.UTF-8")                        -- 设置区域为美式英语
-- 获取当前时间戳
os.time()                                          -- 返回当前秒级时间戳
-- 生成临时文件名
os.tmpname()                                       -- 返回唯一临时文件名（不创建文件）
```

## 调试库
```lua
-- 获取钩子设置
debug.gethook()                                    -- 返回当前钩子函数
-- 获取函数信息
debug.getinfo(print)                               -- 返回包含信息的表
-- 获取局部变量
debug.getlocal(1, 1)                               -- 获取当前函数的第一个局部变量
-- 获取元表
debug.getmetatable("test")                         -- 返回字符串的元表
-- 获取注册表
debug.getregistry()                                -- 返回全局注册表
-- 获取上值
debug.getupvalue(math.sin, 1)                      -- 返回sin函数的上值
-- 获取用户值
debug.getuservalue(io.stdout)                      -- 返回文件对象的用户值
-- 设置调试钩子
debug.sethook(print, "crl", 100)                   -- 每100条指令触发钩子
-- 设置局部变量
debug.setlocal(1, 1, "new")                        -- 修改局部变量值
-- 设置元表
debug.setmetatable({}, {})                         -- 设置表的元表
-- 设置上值
debug.setupvalue(math.randomseed, 1, os.time())    -- 修改随机种子
-- 设置用户值
debug.setuservalue(io.stdin, {})                   -- 设置用户自定义数据
-- 获取调用栈
debug.traceback()                                  -- 返回当前堆栈信息
-- 获取上值唯一标识
debug.upvalueid(function() local x=1 end, 1)       -- 返回上值的唯一标识符
-- 关联两个上值
debug.upvaluejoin(f1, 1, f2, 1)                    -- 使两个函数共享上值
```

## UTF-8 库
```lua
-- 由码点生成UTF-8字符
utf8.char(0x4E2D)                                  -- 返回"中"
-- UTF-8字符模式（常量）
utf8.charpattern                                   -- 返回"[\\0-\\x7F\\xC2-\\xFD][\\x80-\\xBF]*"
-- 获取字符码点范围
utf8.codepoint("中文",1)                           -- 返回20013和3（下一个位置）
-- 迭代UTF-8字符
for p,c in utf8.codes("Aç") do print(c) end        -- 输出65,231
-- 计算字符数量
utf8.len("汉字")                                   -- 返回2（实际字符数）
-- 查找字节位置
utf8.offset("a§",2)                               -- 返回3（第2字符的字节起始位置）
```

## 包管理
```lua
-- 包配置信息（常量）
package.config                                     -- 包含路径分隔符等配置
-- 已加载模块表（常量）
package.loaded                                     -- 指向c模块 (package.loaded.c)
-- 动态加载C库
package.loadlib("lib.so", "luaopen_mylib")         -- 返回加载函数
-- 模块搜索路径（常量）
package.path = "?.lua;./lib/?.lua"                 -- 设置Lua模块搜索路径
-- 预加载模块表（常量）
package.preload.mymod = function() return {} end   -- 预定义模块加载器
-- 模块搜索器列表（常量）
package.searchers[3] = function() end              -- 添加自定义搜索器
-- 路径搜索文件
package.searchpath("mymod", package.path)          -- 返回模块文件路径
```