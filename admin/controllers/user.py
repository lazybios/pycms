#encoding=utf-8

import web
from web import form

from admin import render
from app.helpers import validator, session
from app.models import user as user_model

vusername = form.regexp(r'^[A-z\-_0-9]{4,16}$', '必须为包含英文或数字、_、-的4-16个字符')

user_form = form.Form(
    form.Textbox('username', validator.not_empty, vusername , description='用户名'),
    form.Password('password',  description='密码'),
    form.Password('confirm_password', description='确认密码'),
    form.Textbox('email', validator.not_empty, validator.email , description='电子邮件'),
    form.Dropdown('status', args=[(k, user_model.status_list[k]) for k in user_model.status_list], description='状态'),
)

profile_form = form.Form(
    form.Textbox('username', validator.not_empty, vusername , description='用户名'),
    form.Password('password',  description='密码'),
    form.Password('confirm_password', description='确认密码'),
    form.Textbox('email', validator.not_empty, validator.email , description='电子邮件'),
)

class Index:
    def GET(self, page=1):
        page = int(page)
        s = web.input().get('s')
        where = vars = None
        search = ''
        if not s is None and s.strip():
            if s.find('@'):
                where = 'email LIKE $s'
            else:
                where = 'username LIKE $s'
            vars = {'s': '%' + s + '%'}
            search = s
        users, total = user_model.get_users(page, limit=4, where=where, vars=vars)
        return render.user_index(users, page, total, per_num=4, search=search)

    def POST(self):
        doaction = web.input().get('doaction')
        action = web.input().get('action')
        ids = web.input(id=[]).get(id, [])
        if doaction == 'doaction' and action != '-1' and ids:
            if action == 'delete':
                count = user_model.del_user(ids)
                if not count is False:
                    session.set_flash('已删除%d个用户' % count, 'success')

        raise web.seeother('/user')


class Edit:
    def GET(self, id):
        id = int(id)
        data = user_model.get_user(id, what='id, username, email, status')
        if data is None:
            session.set_flash('没有找到该用户', 'error')
            raise web.seeother('/user')
        else:
            form = user_form()
            form.fill(data)
            return render.user_edit(form, id)

    def POST(self, id):
        id = int(id)
        data = user_model.get_user(id, what='id, username, email')
        if data is None:
            session.set_flash('没有找到该用户', 'error')
            raise web.seeother('/user')
        else:
            form = user_form()

            username = web.input().get('username', '')
            email = web.input().get('email', '')
            password = web.input().get('password', '')
            confirm_password = web.input().get('confirm_password', '')

            if username != data.username:
                form.username.validators += (validator.unique('users', 'username'),)

            if email != data.email:
                form.email.validators += (validator.unique('users', 'email'),)

            if password != '' or confirm_password != '':
                form.password.validators += (validator.not_empty,validator.between(6, 16),)
                form.confirm_password.validators += (validator.not_empty, validator.match(password),)

            if not form.validates():
                return render.user_edit(form, id)
            else:
                data = {
                        'username': form.d.username,
                        'email': form.d.email,
                        'status': int(form.d.status),
                        }

                if password != '':
                    data.update({'password': password})

                if user_model.update_user(id, **data):
                    session.set_flash('用户编辑成功', 'success')
                else:
                    session.set_flash('用户编辑失败', 'error')

                raise web.seeother('/user/edit/%d' % id)


class Add:
    def GET(self):
        form = user_form()
        return render.user_add(form)

    def POST(self):
        form = user_form()

        form.username.validators += (validator.unique('users','username'),)
        form.email.validators += (validator.unique('users', 'email'),)
        form.password.validators += (validator.not_empty,validator.between(6, 16),)
        form.confirm_password.validators += (validator.not_empty, validator.match(web.input().get('password')),)

        if not form.validates():
            return render.user_add(form)

        user_id = user_model.new_user(form.d.username, form.d.password, form.d.email, status=int(form.d.status))
        if user_id:
            session.set_flash('用户添加成功', 'success')
            raise web.seeother('/user/add')
        else:
            session.set_flash('用户添加失败', 'error')
            raise web.seeother('/user/add')


class Profile:
    def GET(self):
        id = int(web.ctx.session.user_id)
        data = user_model.get_user(id, what='id, username, email')
        if data is None:
            raise web.notfound()
        else:
            form = profile_form()
            form.fill(data)
            return render.user_profile(form)

    def POST(self):
        id = int(web.ctx.session.user_id)
        data = user_model.get_user(id, what='id, username, email')
        if data is None:
            raise web.notfound()
        else:
            form = profile_form()

            username = web.input().get('username', '')
            email = web.input().get('email', '')
            password = web.input().get('password', '')
            confirm_password = web.input().get('confirm_password', '')

            if username != data.username:
                form.username.validators += (validator.unique('users', 'username'),)

            if email != data.email:
                form.email.validators += (validator.unique('users', 'email'),)

            if password != '' or confirm_password != '':
                form.password.validators += (validator.not_empty,validator.between(6, 16),)
                form.confirm_password.validators += (validator.not_empty, validator.match(password),)

            if not form.validates():
                return render.user_profile(form)
            else:
                data = {
                    'username': form.d.username,
                    'email': form.d.email,
                }

                if password != '':
                    data.update({'password': password})

                if user_model.update_user(id, **data):
                    session.set_flash('资料编辑成功', 'success')
                else:
                    session.set_flash('资料编辑失败', 'error')

                raise web.seeother('/user/profile')


class Delete:
    def GET(self):
        pass

    def POST(self):
        pass
