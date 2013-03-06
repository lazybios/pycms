#encoding=utf-8
import web
from web import form
from datetime import datetime

from admin import render
from app.helpers import validator, session
from app.models import post as post_model
from app.models import category as category_model

post_form = form.Form(
    form.Hidden('id'),
    form.Textbox('title', validator.not_empty, description='标题', class_='input-block-level'),
    form.Textarea('content', description='内容', rows=20, cols=30, class_='input-block-level'),
    form.Textbox('slug', description='别名'),
    form.Dropdown('category_ids', category_model.get_category_dropdown(model='post'), description='分类', class_='input-block-level', multiple='multiple'),
    form.Textbox('tags', description='标签', class_='input-block-level'),
    form.Dropdown('status', post_model.status_list.items(), description='状态'),
    form.Dropdown('comment_status', post_model.comment_status_list.items(), description='评论状态', value=post_model.COMMENT_STATUS_OPEN),
    form.Textbox('published', description='发布时间'),
)

class Index:
    def GET(self):
        pass

    def POST(self):
        pass

class Add:
    def GET(self):
        form = post_form()
        return render.post_add(form)

    def POST(self):
        form = post_form()
        data = web.input(category_ids=[])

        if 'slug' in data and data['slug'].strip():
            data['slug'] = data['slug'].strip()
            form.slug.validators = (validator.unique('posts', 'slug'), )

        if 'category_ids' in data:
            data['category_ids'] = [web.intget(category_id, 0)  for category_id in data['category_ids']]

        if not form.validates(data):
            return render.post_add(form)

        data['user_id'] = 1

        if post_model.new_post(**data):
            session.set_flash('添加文章成功', 'success')
        else:
            session.set_flash('添加文章失败', 'error')

        raise web.seeother('/post/add')

class Edit:
    def GET(self, id):
        post = post_model.get_post(int(id), status=None)
        if not post:
            raise web.notfound()

        categories = post['categories']
        tags = post['tags']

        if categories:
            post['category_ids'] = [category['id'] for category in categories]

        if tags:
            post['tags'] = ','.join([tag['name'] for tag in tags])
        else:
            post['tags'] = ''

        form = post_form()
        form.fill(post)
        return render.post_edit(form)

    def POST(self):
        pass

class Delete:
    def GET(self):
        pass

    def POST(self):
        pass

