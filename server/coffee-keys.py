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
                        return {'status': True, 'data': '验证成功'}
                else:
                    return 'server error', 500
        else:
            return errors.recaptcha_verify_failed
    else:
        return errors.recaptcha_not_found


@app.route('/api/updateInfo', methods=['POST'])
def addNew():
    g_recaptcha_response = request.form['g-recaptcha-response']
    if recaptcha.verify(g_recaptcha_response):
        u_name = request.form['name']
        u_mail = request.form['mail']
        password = request.form['password'] if request.form['password'] == request.form['repeat-password'] else False
        if not password:
            return redirect(f'/updataKey.html?msg=输入的密码不相同', 302)
        u_password = database.encrypt_password(
            request.form['password'].encode())  # BASE64 交给 database.py
        u_pubkey = request.form['pubkey']
        u_uuid = database.get_u_uuid(u_mail)
        u_date = database.get_u_date()
        id_status, u_id = database.find_ID(u_mail)
        if id_status:
            status, msg = database.update(u_uuid, u_name, u_mail, u_password, u_pubkey, u_date, u_id)
            if status:
                return redirect(f'/searchKey.html?mail={u_mail}&msg=添加成功', 302)
            else:
                return redirect(f'/searchKey.html?mail={u_mail}&msg={msg}', 302)
        else:
            return 'server error', 500
    else:
        return redirect(f'/updataKey.html?msg=reCAPTCHA 令牌无效', 302)


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
