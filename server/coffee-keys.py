import json
import base64

from flask import Flask, redirect, render_template, request

import database
import errors
import recaptcha
import settings

app = Flask(__name__)


@app.route('/api/is_exist', methods=['GET'])
def is_exist():
    status = database.is_exist(request.args['mail'])
    return {'status': status}


@app.errorhandler(404)
def page_not_found(error):
    return render_template('error.html', code='404 Not Found', error=error), 404


@app.route('/api/newKey', methods=['POST'])
def addNew():
    g_recaptcha_response = request.form['g-recaptcha-response']
    if recaptcha.verify(g_recaptcha_response):
        u_name = request.form['name']
        u_mail = request.form['mail']
        password = request.form['password'] if request.form['password'] == request.form['repeat-password'] else False
        if not password:
            return redirect(f'/newKey.html?msg=输入的密码不相同', 302)
        u_password = database.encrypt_password(
            request.form['password'].encode())  # BASE64 交给 database.py
        u_pubkey = request.form['pubkey']
        u_uuid = database.get_u_uuid(u_mail)
        u_date = database.get_u_date()
        status, msg = database.add_new(
            u_uuid, u_name, u_mail, u_password, u_pubkey, u_date)
        if status:
            return redirect(f'/searchKey.html?mail={u_mail}&msg=添加成功', 302)
        else:
            return redirect(f'/searchKey.html?mail={u_mail}&msg={msg}', 302)
    else:
        return redirect(f'/newKey.html?msg=reCAPTCHA 令牌无效', 302)


@app.route('/api/searchKey', methods=['GET'])
def searchKey():
    u_mail = request.args['mail']
    exist = database.is_exist(u_mail)
    if exist:
        status, data = database.find(u_mail)
        return {'status': status, 'data': data}
    else:
        return {'status': exist, 'data': '信息不存在'}


@app.route('/api/verifyPassword', methods=['GET'])
def verifyPassword():
    if 'g-recaptcha-response' in request.args:
        g_recaptcha_response = request.args['g-recaptcha-response']
        if recaptcha.verify(g_recaptcha_response):
            u_mail = request.args['mail']
            u_password = request.args['password']
            if database.is_exist(u_mail):
                d_status, d_password = database.query_password(u_mail)
                if d_status:
                    if database.check_password(u_password, base64.b64decode(d_password).decode()):
                        return {'status': True, 'data': '认证成功'}
                    else:
                        return {'status': False, 'data': '认证失败'}
                else:
                    return {'status': False, 'data': '服务器错误'}
            else:
                return {'status': False, 'data': '邮箱不存在'}
        else:
            return errors.recaptcha_verify_failed
    else:
        return errors.recaptcha_not_found


@app.route('/api/updateInfo', methods=['POST'])
def update():
    if 'g-recaptcha-response' in request.form:
        g_recaptcha_response = request.form['g-recaptcha-response']
        if recaptcha.verify(g_recaptcha_response):
            u_name = request.form['name']
            u_mail = request.form['mail']
            u_password = request.form['password']
            origin_mail = request.form['originMail']
            origin_password = request.form['originPassword']
            has_new_password = False if u_password == '' else True
            # 过滤异常请求，分为更改了密码和未更改密码
            if has_new_password:  # 更改了密码
                u_repeat_password = request.form['repeat-password']
                password = u_password if u_password == u_repeat_password else False
                if not password:
                    return redirect(f'/updateInfo.html?msg=输入的密码不相同', 302)
                if database.is_exist(origin_mail):
                    d_status, d_password = database.query_password(origin_mail)
                    if d_status:
                        if not database.check_password(origin_password,
                                                       base64.b64decode(d_password).decode()):
                            return redirect(f'/updateInfo.html?msg=认证失败', 302)
                        else:
                            u_password = database.encrypt_password(
                                u_password.encode())  # 成功
                    else:
                        return redirect(f'/updateInfo.html?msg=原密码查询失败', 302)
                else:
                    return redirect(f'/updateInfo.html?msg=邮箱不存在', 302)
            else:  # 未更改密码
                qp_status, p_data = database.query_password(origin_mail)
                if qp_status:
                    # 成功
                    u_password = base64.b64decode(p_data).decode()
                else:
                    return redirect(f'/updateInfo.html?msg=原密码查询失败', 302)
            # 执行 update
            u_pubkey = request.form['pubkey']
            u_uuid = database.get_u_uuid(u_mail)
            u_date = database.get_u_date()
            id_status, u_id = database.find_ID(origin_mail)
            if id_status:
                status, msg = database.update(
                    u_uuid, u_name, u_mail, u_password, u_pubkey, u_date, u_id)
                if status:
                    return redirect(f'/searchKey.html?mail={u_mail}&msg=更改成功', 302)
                else:
                    return redirect(f'/searchKey.html?mail={u_mail}&msg={msg}', 302)
            else:
                return redirect(f'/updateInfo.html?msg=停止你的黑客行为！', 302)
        else:
            return redirect(f'/updateInfo.html?msg=reCAPTCHA 令牌无效，请尝试刷新页面', 302)
    else:
        return redirect(f'/updateInfo.html?msg=reCAPTCHA 令牌未找到，停止你的黑客行为！', 302)


@app.route('/api/deleteInfo', methods=['DELETE'])
def deleteInfo():
    if 'g-recaptcha-response' in request.args:
        g_recaptcha_response = request.args['g-recaptcha-response']
        if recaptcha.verify(g_recaptcha_response):
            u_mail = request.args['mail']
            u_password = request.args['password']
            if database.is_exist(u_mail):
                d_status, d_password = database.query_password(u_mail)
                if d_status:
                    if database.check_password(u_password, base64.b64decode(d_password).decode()):
                        id_status, u_id = database.find_ID(u_mail)
                        if id_status:
                            database.delete(u_id)
                            status, msg = database.reformat_id()
                            if status:
                                return {'status': True, 'data': '重新排序成功'}
                            else:
                                return {'status': True, 'data': msg}
                            return {'status': True, 'data': '删除成功'}
                        else:
                            return {'status': False, 'data': '服务器错误'}
                    else:
                        return {'status': False, 'data': '密码错误'}
                else:
                    return {'status': False, 'data': '服务器错误'}
            else:
                {'status': False, 'data': '邮箱不存在'}
        else:
            return errors.recaptcha_verify_failed
    else:
        return errors.recaptcha_not_found


@app.route('/api/recaptcha/getSiteKey')
def recaptcha_getSiteKey():
    return settings.reCAPTCHA.siteKey


@app.route('/api/Ui/common')
def ui_common():
    return settings.Ui.common


@app.route('/api/Ui/index')
def ui_index():
    return json.dumps(settings.Ui.index)


if __name__ == "__main__":
    app.run('0.0.0.0', 84, debug=True)
