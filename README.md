# coffee-keys
A Key Server, which can store and distribute public key safely and quickly.  
一个公钥服务器，可以安全、快速地存储和分发公钥。

![Python3](https://img.shields.io/badge/Python-3-python?color=3776AB&&logo=python) ![GPLv3](https://img.shields.io/github/license/super-coffee/coffee-keys)

简体中文 | [English](/README_en.md)

---

UI 正在重构，请参考 [super-coffee/coffee-keys-go](https://github.com/super-coffee/coffee-keys-go)

---
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

