#coding=utf-8
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
    try:
        status, role = is_exist(u_mail)
        if status and role != -1:
            m = 'Data has already exists'
            print(m)
            return False, m
        u_password = base64.b64encode(u_password).decode()
        cursor.execute(f"SELECT id from `{settings.Database.user_table}` WHERE role = -1")
        result = cursor.fetchall()
        if len(result) > 0:
            p_id = result[0][0]
            update(u_uuid, u_name, u_mail, u_password, u_pubkey, u_date, p_id)
            cursor.execute(f"""UPDATE `{settings.Database.user_table}` 
                                SET role=0 WHERE id=%s""", (p_id))
        else:
            cursor.execute(f"""INSERT INTO `{settings.Database.user_table}` (`uuid`, `name`, `mail`, `password`, `date`)
                                VALUES (%s, %s, %s, %s, %s)""", (u_uuid, u_name, u_mail, u_password, u_date))
            _, u_id = find_uid(u_mail)
            cursor.execute(f"""INSERT INTO `{settings.Database.pubkey_table}` (`u_id`, `pubkey`)
                                VALUES ({u_id}, %s)""", (u_pubkey))
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
    try:
        cursor.execute(f"""SELECT role FROM `{settings.Database.user_table}`
                            WHERE mail = %s""", (u_mail))
        # 获取所有记录列表
        results = cursor.fetchall()
        status = len(results) > 0
        return True if status else False, results[0][0] if status else 0
    except Exception as e:
        print(repr(e))
        return True


def find(u_mail):
    """根据邮箱查询，只返回第一个公钥"""
    db.ping(reconnect=True)
    try:
        cursor.execute(f"""SELECT id, name, mail, date, password FROM `{settings.Database.user_table}`
                            WHERE mail = %s""", (u_mail))
        results = cursor.fetchall()
        row = results[0]
        u_id, name, mail, date, password = row
        cursor.execute(f"""SELECT pubkey FROM `{settings.Database.pubkey_table}`
                            WHERE u_id = %s""", u_id)
        results = cursor.fetchall()
        keynum = len(results)
        data = {
            'name': name,
            'mail': mail,
            'pubkey': results,
            'date': str(date),
            'key_num': keynum,
            'password': password
        }
        return True, data
    except Exception as e:
        print(repr(e))
        return False, errors.hack_warning


def find_uid(u_mail):
    """根据邮箱查询 id 字段"""
    db.ping(reconnect=True)
    try:
        cursor.execute(f"""SELECT id FROM `{settings.Database.user_table}`
                            WHERE mail = %s""", (u_mail))
        result = cursor.fetchall()
        return True, result[0][0]
    except Exception as e:
        print(repr(e))
        return False, errors.hack_warning


def find_kid(index, uid):
    """根据用户 id 查询公钥 id 字段"""
    db.ping(reconnect=True)
    try:
        cursor.execute(f"""SELECT id FROM `{settings.Database.pubkey_table}`
                            WHERE u_id = %s""", (uid))
        result = cursor.fetchall()[index]
        kid = result[0]
        return True, kid
    except Exception as e:
        print(repr(e))
        return False, errors.info_not_found


def update(u_uuid, u_name, u_mail, u_password, u_pubkey, u_date, u_id):
    """根据 id 字段更新数据库"""
    db.ping(reconnect=True)
    try:
        if type(u_password) == str:
            u_password = u_password.encode()
        u_password = base64.b64encode(u_password).decode()
        cursor.execute(f"""UPDATE `{settings.Database.user_table}` SET uuid=%s, name=%s, mail=%s, password=%s,
                            date=%s WHERE id={u_id}""", (u_uuid, u_name, u_mail, u_password, u_date))
        _, kid = find_kid(0, u_id)
        cursor.execute(f"""UPDATE `{settings.Database.pubkey_table}`
                            SET pubkey=%s WHERE id = %s""", (u_pubkey, kid))
        db.commit()
        return True, 'ok'
    except Exception as e:
        db.rollback()
        print(e)
        return False, repr(e)


def delete(u_id):
    """根据 id 字段删除记录"""
    db.ping(reconnect=True)
    try:
        cursor.execute(f"""UPDATE `{settings.Database.user_table}` 
                                SET role=-1 WHERE id=%s""", (u_id))
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