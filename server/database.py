import base64
import datetime
import time
import uuid

import bcrypt
import pymysql

import errors
import settings

# 连接数据库
db = pymysql.connect(host=settings.Database.host,
                     port=settings.Database.port,
                     user=settings.Database.username,
                     password=settings.Database.password,
                     db=settings.Database.db)
print('MySQL connected')
cursor = db.cursor()


def get_u_uuid(mail_addr):
    """传入邮箱，返回 UUID (str)"""
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, mail_addr))


def get_u_date():
    """返回 YYYY-mm-dd HH:MM:SS"""
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


def check_password(u_password, d_password):
    """
    使用 Bcrypt 验证密码
    :param u_password: 用户输入的密码
    :param d_password: 数据库中的密码
    :return: Boolean
    """
    print(u_password)
    print(d_password)
    return bcrypt.checkpw(u_password.encode(), d_password.encode())


def encrypt_password(original_password):
    """使用 Bcrypt 加密密码"""
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(original_password, salt)
    return hashed_password


def reconnect():
    """重新连接数据库"""
    try:
        db.ping(reconnect=True)
        return True, 'reconnected'
    except Exception as e:
        return False, e


def add_new(u_uuid, u_name, u_mail, u_password, u_pubkey, u_date):
    """新增数据"""
    db.ping(reconnect=True)
    sql = f"""INSERT INTO `{settings.Database.table}` (`uuid`, `name`, `mail`, `password`, `pubkey`, `date`)
    VALUES (%s, %s, %s, %s, %s, %s)"""
    try:
        if is_exist(u_mail):
            m = '此邮箱已经存在'
            print(m)
            return False, m
        u_password = base64.b64encode(u_password).decode()
        cursor.execute(sql, (u_uuid, u_name, u_mail,
                             u_password, u_pubkey, u_date))
        # 提交到数据库执行
        db.commit()
        m = 'Added'
        print(m)
        return True, m
    except Exception as e:
        # 如果发生错误则回滚
        db.rollback()
        print(e)
        return False, e


def is_exist(u_mail):
    """
    根据邮箱查询，检查是否存在；
    False 是不存在
    """
    db.ping(reconnect=True)
    sql = f"""SELECT * FROM `{settings.Database.table}` WHERE mail = %s"""
    try:
        cursor.execute(sql, u_mail)
        # 获取所有记录列表
        results = cursor.fetchall()
        return True if len(results) > 0 else False
    except Exception as e:
        print(repr(e))
        return True


def find(u_mail):
    """根据邮箱查询，不返回 password 字段"""
    db.ping(reconnect=True)
    sql = f"""SELECT name, mail, pubkey, date, password FROM `{settings.Database.table}` WHERE mail = %s"""
    try:
        cursor.execute(sql, u_mail)
        # 获取所有记录列表
        results = cursor.fetchall()
        row = results[0]
        data = {
            'name': row[0],
            'mail': row[1],
            'pubkey': row[2],
            'date': str(row[3]),
            'password': row[4]
        }
        return True, data
    except Exception as e:
        print(repr(e))
        return False, errors.hack_warning


def find_ID(u_mail):
    """根据邮箱查询 id 字段"""
    db.ping(reconnect=True)
    sql = f"""SELECT id FROM `{settings.Database.table}` WHERE mail = %s"""
    try:
        cursor.execute(sql, u_mail)
        result = cursor.fetchall()
        return True, result[0][0]
    except Exception as e:
        print(repr(e))
        return False, errors.hack_warning


def update(u_uuid, u_name, u_mail, u_password, u_pubkey, u_date, u_id):
    """根据 id 字段更新数据库"""
    db.ping(reconnect=True)
    sql = f"""UPDATE `{settings.Database.table}` SET uuid=%s, name=%s, mail=%s,
            password=%s, pubkey=%s, date=%s WHERE id={u_id}"""
    try:
        u_password = base64.b64encode(u_password).decode()
        cursor.execute(sql, (u_uuid, u_name, u_mail,
                             u_password, u_pubkey, u_date))
        db.commit()
        return True, 'ok'
    except Exception as e:
        db.rollback()
        print(e)
        return False, repr(e)


def delete(ID):
    """根据 id 字段删除记录"""
    db.ping(reconnect=True)
    sql = """DELETE FROM `{table}` WHERE id = {id}""".format(
        table=settings.Database.table, id=ID)
    try:
        print(sql)
        cursor.execute(sql)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        return False, repr(e)


def reformat_id(u_id):
    """重新排列 id 列"""
    db.ping(reconnect=True)
    if not u_id % 100:
        try:
            cursor.execute("ALTER TABLE `{table}` DROP `id`;".format(
                table=settings.Database.table))
            cursor.execute("ALTER TABLE `{table}` ADD `id` INT NOT NULL FIRST;".format(
                table=settings.Database.table))
            cursor.execute("ALTER TABLE `{table}` MODIFY COLUMN `id` INT NOT NULL \
                AUTO_INCREMENT,ADD PRIMARY KEY(id);".format(table=settings.Database.table))
            db.commit()
            return True, 'reformated'
        except Exception as e:
            print(e)
            return False, repr(e)
    else:
        return True, '不需要重新排序'


if __name__ == "__main__":
    pass