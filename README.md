# coffee-keys
A Key Server, which can store and distribute public key safely and quickly.  
一个公钥服务器，可以安全、快速地存储和分发公钥。

![Python3](https://img.shields.io/badge/Python-3-python?color=3776AB&&logo=python) ![GPLv3](https://img.shields.io/github/license/super-coffee/coffee-keys)

[English Readme](#English)

---
# 简体中文
## 特点 👍
- 轻巧：体积仅有 1.5Mb，采用前后端分离的架构，可拓展性强
- 快捷：无需繁琐的注册，开箱即用
- 安全：个人信息加密保存，防止 SQL 注入，并使用 [reCAPTCHA](https://www.google.com/recaptcha) 防止 CC 攻击
- 优美：界面采用 [Layui](https://www.layui.com/) 设计；极简，却又不失饱满的内在

## 环境要求 🌵
- Python 3.6 +
- MySQL 5.3 +
- 一个支持反向代理的 Web 服务器（如 Caddyserver, Nginx 等）
- **一个脑子**

## 用法  😋
1. 从 [Releases 页面](https://github.com/super-coffee/coffee-keys/releases) 下载最新版本的 Coffee Keys
2. 解压下载到的文件
3. 注册你的 [Google reCAPTCHA](https://www.google.com/recaptcha/admin) 密钥，将 database.sql 导入你的数据库
4. 按提示修改 `./server/settings.template.py`，删除或修改 `./web/index.html` 的备案信息
5. 运行以下命令，需要保持后台运行（Linux 推荐使用 screen，其他方法也可）
    ``` bash
    pip3 install -r requirements.txt
    python3 coffee-keys.py
    ```
    服务将会在 `:84` 端口上开启，你需要保证本端口无占用
6. 使用你的 Web 服务器进行反向代理，以 Caddyserver 为例：
    ``` caddyfile
    your.domain {
        root ./web
        file_server
    }
    your.domain/api/* {
        reverse_proxy /api/* localhost:84
    }
    ```
    这只是一个示例，你可以根据实际情况进行调整
7. 访问 `your.domain`，查看效果

---
# English
## Features 👍
- *Lightweight*: the code size is only 1.5Mb, and the web level and the server level are separated, with high scalability.
- *Fast*: no need for tedious registration, use it out of the box.
- *Security*: Prevent SQL injection and use [reCAPTCHA](https://www.google.com/recaptcha) to prevent CC attacks.
- *Beauty*: The interface is designed by [Layui](https://www.layui.com/). Minimalist, without losing the fullness of the inside
(Minimalist, yet full of inner)
## Environmental requirements 🌵
- Python 3.6 +
- MySQL 5.3 +
- A web server that supports reverse proxy (such as Nginx)
- **Your BRAIN**
## Usage  😋
1. Download latest relase from [Github Releases](https://github.com/super-coffee/coffee-keys/releases)
2. Unzip it `tar -zxvf filemane.zip`
3. Register reCAPTCHA key from [Google reCAPTCHA](https://www.google.com/recaptcha/admin). If you are in GFW, please use special Way to get. And then import `database.sql` to your database.
4. Edit `./server/settings.template.py` , delete or modify './web/index.html', as prompted
5. Command (Recommand `screen` in linux)
    ``` bash
    pip3 install -r requirements.txt
    python3 coffee-keys.py
    ```
    The service will run in `:84` port, so you should keep it free.
6. Use your web server for reverse proxy, for example (Caddyserver):
    ``` caddyfile
    your.domain {
        root ./web
        file_server
    }
    your.domain/api/* {
        reverse_proxy /api/* localhost:84
    }
    ```
    This is just an example. You can adjust it according to the actual situation
7. Visit your web, enjoy  ;>

## Help us improve translation
If you find that our translation is grammatically incorrect, welcome to open a new pull request. We will thank for you.
