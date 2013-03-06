#encoding=utf-8
import web
from datetime import datetime

from app.models import tag as tag_model
from app.models import category as category_model
from config import db

STATUC_DRAFT = 0
STATUC_PUBLISH = 1

status_list = {
    STATUC_DRAFT: '草稿',
    STATUC_PUBLISH: '公开',
}

COMMENT_STATUS_OPEN = 1
COMMENT_STATUS_CLOSE = 0

comment_status_list = {
    COMMENT_STATUS_OPEN: '开启',
    COMMENT_STATUS_CLOSE: '关闭',
}

def get_post(id=None, slug=None, status=STATUC_PUBLISH ):
    where = {}
    vars = {}

    if id is not None:
        where['id'] = id

    if slug is not None:
        where['slug'] = slug

    if status is not None:
        where['status'] = status

    try:
        post = db.where('posts', limit=1, **where)[0]
        #post['user'] = user_model.get_user(post['user_id'])
        post['categories'] = category_model.get_categories_by_object(post['id'])
        post['tags'] = tag_model.get_tags_by_object(post['id'], 'post')
        return post
    except IndexError:
        return False

def filter_values(values):
    fields = ['title', 'content', 'slug', 'tags', 'category_ids', 'user_id', 'published', 'status', 'comment_status']
    for field in values.keys():
        if field not in fields:
            del values[field]

def new_post(**values):
    filter_values(values)
    tags = values.pop('tags', None)
    category_ids = values.pop('category_ids', None)

    values['created'] = values['modified'] = datetime.utcnow()

    t = db.transaction()
    try:
        web.debug('test')
        post_id = db.insert('posts', **values)

        web.debug('test2')
        web.debug(tags)
        if tags:
            tag_model.save_tag_relationships(post_id, 'post', tags, new=True)

        if category_ids:
            category_model.save_category_relationships(post_id, category_ids, new=True)
    except:
        t.rollback()
        return False
    else:
        t.commit()
        return post_id

def update_post(id=None, where=None, vars=None, **values):
    if id is not None:
        where = 'id=$id'
        vars = {'id': id}

    filter_values(values)
    tags = values.pop('tags', None)
    category_ids = values.pop('category_ids', None)

    values['modified'] = datetime.utcnow()
    t = db.transaction()
    try:
        db.update('posts', where=where, vars=vars, **values)

        if tags:
            tag_model.save_tag_relationships(post_id, 'post', tags)

        if category_ids:
            category_model.save_category_relationships(post_id, category_ids)
    except:
        t.rollback()
        return False
    else:
        t.commit()
        return True

def delet_post(id=None):
    return
