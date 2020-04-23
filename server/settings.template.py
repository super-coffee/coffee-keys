# IMPORTANT
# Please rename this file to 'settings.py'
# You should modify the following according to the actual situation before you deploy this project

class Database:
    host = 'localhost'
    port = 3306
    username = 'coffee-keys'
    password = 'PASSWORD'
    db = 'coffee-keys'
    table = 'coffee-keys'


class Ui:
    common = {
        'displyName': 'Coffee Keys',
        'copyrightText': """2020 © super-coffee"""
    }

    index = [
        {
            'name': '注册 Coffee Key',
            'url': './newKey.html',
            'line1': '注册一个 Coffee Key',
            'line2': '在这个页面你可以上传你的公钥'
        },
        {
            'name': '查找 Coffee Key',
            'url': './searchKey.html',
            'line1': '寻找你朋友的 Coffee Key',
            'line2': '在这个页面你可以找到你想找的公钥'
        }
    ]


class reCAPTCHA:
    siteKey = 'SECRET'
    serverKey = 'SECRET'