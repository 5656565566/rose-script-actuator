# rose-script-actuator
一个使用 lua 语言编写简单脚本的 自动化控制 支持 adb windows 等

使用 Poetry 包管理器

# 运行

## 前往 Releases 下载最新版本
参考 [Releases](https://github.com/5656565566/rose-script-actuator/releases) 下载最新版本的可执行文件。支持 Linux Windows

## 使用源码运行

从当前仓库克隆代码，并安装依赖。

## 环境依赖
安装 Python 3.10 及以上版本，并安装 Poetry 包管理器。可以参考以下链接进行安装：[Poetry 官方文档](https://python-poetry.org/docs/#installation)+

 - 开发
```shell
poetry install
```
 - 使用
```shell
poetry install --no-dev
```

## 运行
```shell
poetry run python actuator
```
直接运行项目