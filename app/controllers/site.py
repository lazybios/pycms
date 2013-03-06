#encoding=utf-8

import web
from web import form

from admin import render
from app.helpers import validator, session
from app.models import user as user_model

login_form = form.Form(
    form.Textbox('username', validator.not_empty, description='用户名', class_='input-block-level', placeholder='用户名'),
    form.Password('password', validator.not_empty, descriptin='密码', class_='input-block-level', placeholder='密码'),
)

vusername = form.regexp(r'^[A-z\-_0-9]{6,16}$', '必须为包含英文或数字、_、-的6-16个字符')

register_form = form.Form(
    form.Textbox('username', validator.not_empty, vusername, validator.unique('users', 'username'), description='用户名', class_='input-block-level'),
    form.Password('password', validator.not_empty, validator.between(6, 16), description='密码',  class_='input-block-level'),
    form.Password('confirm_password', validator.not_empty, description='确认密码', class_='input-block-level'),
    form.Textbox('email', validator.not_empty, validator.email, validator.unique('users', 'email'), description='电子邮件', class_='input-block-level'),
)

forget_password_form = form.Form(
    form.Textbox('email', validator.not_empty, validator.email, description='电子邮件', class_='input-block-level'),
)

reset_password_form = form.Form(
    form.Password('password', validator.not_empty, validator.between(6, 16), description='密码',  class_='input-block-level'),
    form.Password('confirm_password', validator.not_empty, description='确认密码', class_='input-block-level'),
)

class Register:
    def GET(self):
        form = register_form()
        return render.register(form)

    def POST(self):
        form = register_form()
        form.confirm_password.validators += (validator.match(web.input().get('password')),)
        if not form.validates():
            return render.register(form)

        username = form.d.username
        email = form.d.email
        password = form.d.password
        user_id = user_model.new_user(username, password, email)
        if user_id:
            raise web.seeother('/login')
        else:
            session.set_flash('注册用户失败', 'error')
            raise web.seeother('/register')


class Login:
    def GET(self):
        form = login_form()
        return render.login(form)

    def POST(self):
        form = login_form()
        if not form.validates():
            return render.login(form)
        if session.login(form.d.username, form.d.password):
            raise web.seeother('/admin')
        else:
            session.set_flash('用户名或密码错误', 'error')
            raise web.seeother('/login')

class Forget_password:
    def GET(self):
        form = forget_password_form()
        return render.forget_password(form)

    def POST(self):
        form = forget_password_form()
        if not form.validates():
            return render.forget_password(form)

class Reset_password:
    def GET(self):
        form = reset_password_form()
        return render.reset_password(form)

    def POST(self):
        form = reset_password_form()
        if not form.validates():
            return render.rest_password(form)

class Logout:
    def GET(self):
        session.logout()
        raise web.seeother('/login')

