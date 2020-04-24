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
    """传入邮箱，返回 UUID"""
    return uuid.uuid5(uuid.NAMESPACE_DNS, mail_addr)


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


def add_new(u_uuid, u_name, u_mail, u_password, u_pubkey, u_date):
    """新增数据"""
    sql = f"""INSERT INTO `{settings.Database.table}` (`uuid`, `name`, `mail`, `password`, `pubkey`, `date`)
    VALUES (%s, %s, %s, %s, %s, %s)"""
    try:
        if is_exist(u_mail):
            m = 'Data has already exists'
            print(m)
            return False, m
        cursor.execute(sql, (u_uuid, u_name, u_mail, pymysql.escape_string(base64.b64encode(u_password).decode()),
        u_pubkey, u_date))
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
    False 是不重复
    """
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
    sql = f"""SELECT name, mail, pubkey, date FROM `{settings.Database.table}` WHERE mail = %s"""
    try:
        cursor.execute(sql, u_mail)
        # 获取所有记录列表
        results = cursor.fetchall()
        row = results[0]
        data = {
            'name': row[0],
            'mail': row[1],
            'pubkey': row[2],
            'date': str(row[3])
        }
        return True, data
    except Exception as e:
        print(repr(e))
        return False, errors.hack_warning


def query_password(u_mail):
    """根据邮箱查询 password 字段"""
    sql = f"""SELECT password FROM `{settings.Database.table}` WHERE mail = %s"""
    try:
        cursor.execute(sql, u_mail)
        # 获取所有记录列表
        results = cursor.fetchall()
        print(results[0][0])
        return True, results[0][0]
    except Exception as e:
        print(repr(e))
        return False, errors.hack_warning


def find_ID(u_mail):
    """根据邮箱查询 id 字段"""
    sql = f"""SELECT id FROM `{settings.Database.table}` WHERE mail = %s"""
    try:
        cursor.execute(sql, u_mail)
        result = cursor.fetchall()
        return True, result[0][0]
    except Exception as e:
        print(repr(e))
        return False, errors.hack_warning


def update(u_uuid, u_name, u_mail, u_password, u_pubkey, u_date, u_id):
    """根据id字段更新数据库"""
    sql = f"""UPDATE `{settings.Database.table}` SET uuid=%s, name=%s, mail=%s,
            password=%s, pubkey=%s, date=%s WHERE id={u_id}"""
    try:
        cursor.execute(sql, u_uuid, u_name, u_mail,
        pymysql.escape_string(base64.b64encode(u_password).decode()), u_pubkey, u_date)
        db.commit()
        return True
    except:
        m = 'Error: unable to update data'
        db.rollback()
        print(m)
        return False, m


def delete(ID):
    """根据id字段删除记录"""
    sql = """DELETE FROM `{table}` WHERE id = {id}""".format(
        table=settings.Database.table, id=ID)
    try:
        print(sql)
        cursor.execute(sql)
        db.commit()
        return True
    except:
        m = 'Error: unable to delete data'
        db.rollback()
        print(m)
        return False, m


def confirm_authority(u_mail, u_password):
    """根据mail字段确认操作权限"""
    try:
        status, d_password = query_password(u_mail)
        if status and check_password(u_password, d_password):
            return True
        else:
            return False
    except:
        m = 'Error: unable to confirm authority'
        return False, m


def reformat_id():
    """重新排列 id 列"""
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


if __name__ == "__main__":
    u_datetime = get_u_date()
    _, u_id = find_ID('test')
    print(u_id)
    update('Error', 'Error', 'Error', 'Error'.encode(), 'Error', u_datetime, u_id)
    print(find('test'))
