# coffee-keys
A Key Server, which can store and distribute public key safely and quickly.  
一个公钥服务器，可以安全、快速地存储和分发公钥。

![Python3](https://img.shields.io/badge/Python-3-python?color=3776AB&&logo=python) ![GPLv3](https://img.shields.io/github/license/super-coffee/coffee-keys)

[简体中文](https://github.com/super-coffee/coffee-keys) | English

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
