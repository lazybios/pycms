#encoding=utf-8
import web
from web import form

from admin import render
from app.helpers import validator, session
from app.models import category as category_model

category_form = form.Form(
    form.Textbox('name', validator.not_empty, description='名称'),
    form.Textbox('slug', validator.not_empty, validator.slug,  description='别名'),
    form.Dropdown('parent_id', [(0, '无')], description='父级分类'),
    form.Textarea('description', description='描述', rows=10, cols=20, class_='input-xxlarge'),
)

class Index:
    def GET(self, model):
        category_setting = category_model.get_category_setting(model)
        if category_setting is None:
            raise notfound()

        categories = category_model.get_category_list(model)
        return render.category_index(categories, model, category_setting)

    def POST(self, model):
        category_setting = category_model.get_category_setting(model)
        if category_setting is None:
            raise notfound()

        doaction = web.input().get('doaction')
        action = web.input().get('action')
        ids = web.input(id=[]).get('id')
        if doaction == 'doaction' and action != '-1' and ids:
            if action == 'delete':
                count = category_model.del_category(ids)
                if not count is False:
                    session.set_flash('已删除%d个%s' % (count, category_setting['label']), 'success')

        raise web.seeother('/%s/category' % model)

class Edit:
    def GET(self, model, id):
        id = int(id)

        category_setting = category_model.get_category_setting(model)
        if category_setting is None:
            raise web.notfound()

        category = category_model.get_category(id)

        if category is None:
            utils.set_flash('没有找到该%s' % category_setting['label'], 'error')
            raise web.seeother('/%s/category' % model)
        else:
            form = category_form()
            form.parent_id.args += category_model.get_category_dropdown(model)
            form.fill(category)
            return render.category_edit(form, model, category_setting, id)

    def POST(self, model, id):
        id = int(id)
        category_setting = category_model.get_category_setting(model)

        if category_setting is None:
            raise web.notfound()

        category = category_model.get_category(id)

        if category is None:
            session.set_flash('没有找到该%s' % category_setting['label'], 'error')
            raise web.seeother('/%s/category' % model)
        else:
            values = {
                'name': web.input().get('name'),
                'slug': web.input().get('slug'),
                'parent_id': web.intget(web.input().get('parent_id'), 0),
                'description': web.input().get('description'),
            }

            form = category_form()
            form.parent_id.args += category_model.get_category_dropdown(model)

            if values['slug'] != category['slug']:
                form.slug.validators += (validator.unique('categories', 'slug', where='model=$model', vars={'model': model}),)
            else:
                del values['slug']

            source = web.input()
            if source.get('parent_id') is not None:
                source['parent_id'] = web.intget(source['parent_id'])

            if not form.validates(source):
                return render.category_edit(form, model, category_setting, id)

            if category_model.update_category(model, id, **values) is not False:
                session.set_flash('编辑%s成功' % category_setting['label'], 'success')
            else:
                session.set_flash('编辑%s失败' % category_setting['label'], 'error')

            raise web.seeother('/%s/category/edit/%d' % (model, id))

class Add:
    def GET(self, model):
        category_setting = category_model.get_category_setting(model)
        if category_setting is None:
            raise web.notfound()

        form = category_form()
        form.parent_id.args += category_model.get_category_dropdown(model)

        return render.category_add(form, model, category_setting)

    def POST(self, model):
        category_setting = category_model.get_category_setting(model)
        if category_setting is None:
            raise notfound()

        form = category_form()
        form.parent_id.args += category_model.get_category_dropdown(model)
        form.slug.validators += (validator.unique('categories', 'slug', where='model=$model', vars={'model': model}),)

        source = web.input()
        if source.get('parent_id') is not None:
            source['parent_id'] = web.intget(source['parent_id'])

        if not form.validates(source):
            return render.category_add(form, model, category_setting)

        if category_model.new_category(model, form.d.name, form.d.slug, form.d.parent_id, form.d.description):
            session.set_flash('添加%s成功' % category_setting['label'], 'success')
        else:
            session.set_flash('添加%s失败' % category_setting['label'], 'error')

        raise web.seeother('/%s/category' % model)

class Delete:
    def GET(self):
        pass

    def POST(self):
        pass
