import json
import base64

from flask import Flask, redirect, render_template, request, session
from flask_wtf.csrf import generate_csrf, CSRFProtect

import database
import errors
import recaptcha
import settings

app = Flask(__name__)
csrf = CSRFProtect(app)
# 这个key务必自行修改！
app.secret_key = "jiliguala%%#%^&&"


@csrf.error_handler
def csrf_error(reason):
    return render_template('error.html', code='400 CSRF Error', error=reason), 400


@app.after_request
def after_request(response):
    # 调用函数生成csrf token
    csrf_token = generate_csrf()
    # 设置cookie传给前端
    response.set_cookie('csrf_token', csrf_token)
    return response


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
            return {'status': False, 'data': '输入的密码不相同'}
        u_password = database.encrypt_password(
            request.form['password'].encode())  # BASE64 交给 database.py
        u_pubkey = request.form['pubkey']
        u_uuid = database.get_u_uuid(u_mail)
        u_date = database.get_u_date()
        status, msg = database.add_new(
            u_uuid, u_name, u_mail, u_password, u_pubkey, u_date)
        if status:
            return {'status': True, 'data': u_name}
        else:
            return {'status': False, 'data': msg}
    else:
        return {'status': False, 'data': '令牌无效'}


@app.route('/api/searchKey', methods=['POST'])
def searchKey():
    u_mail = request.form['mail']
    exist = database.is_exist(u_mail)
    if exist:
        status, data = database.find(u_mail)
        del(data['password'])
        return {'status': status, 'data': data}
    else:
        return {'status': exist, 'data': '信息不存在'}


@app.route('/api/verifyPassword', methods=['POST'])
def verifyPassword():
    if 'g-recaptcha-response' in request.form:
        g_recaptcha_response = request.form['g-recaptcha-response']
        if recaptcha.verify(g_recaptcha_response):
            u_mail = request.form['mail']
            u_password = request.form['password']
            if database.is_exist(u_mail):
                d_status, data = database.find(u_mail)
                d_password = data['password']
                u_username = data['name']
                if d_status:
                    if database.check_password(u_password, base64.b64decode(d_password).decode()):
                        return {'status': True, 'data': u_username}
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


@app.route('/api/verifyAuthenticate', methods=['GET'])
def verifyAuthenticate():
    username = session['username']
    if username != "":
        return {'status': True, 'data': username}
    else:
        return errors.permission_forbidden


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
                                return {'status': True, 'data': '删除成功，重新排序成功'}
                            else:
                                return {'status': True, 'data': f'删除成功，重新排序失败：{msg}'}
                        else:
                            return {'status': False, 'data': '服务器错误'}
                    else:
                        return {'status': False, 'data': '密码错误'}
                else:
                    return {'status': False, 'data': '服务器错误'}
            else:
                return {'status': False, 'data': '邮箱不存在'}
        else:
            return errors.recaptcha_verify_failed
    else:
        return errors.recaptcha_not_found


@app.route('/api/logout', methods=['GET'])
def logout():
    session.clear()
    return redirect("/", code=302)


@app.route('/api/recaptcha/getSiteKey')
def recaptcha_getSiteKey():
    return settings.reCAPTCHA.siteKey


@app.route('/api/Ui/common')
def ui_common():
    return settings.Ui.common


@app.route('/api/Ui/index')
def ui_index():
    return json.dumps(settings.Ui.index)


# 登录控制
@app.before_request
def before(*args, **kwargs):
    # allow to visit without login
    allow_visit = [
        '/api/newKey',
        '/api/Ui/index',
        '/api/Ui/common',
        '/api/recaptcha/getSiteKey',
        '/api/verifyPassword',
        '/api/searchKey'
    ]
    if request.path in allow_visit:
        return None
    user = session.get('username')
    if user:
        return None
    return errors.permission_forbidden


if __name__ == "__main__":
    app.run('0.0.0.0', 84, debug=True)
