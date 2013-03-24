#encoding=utf-8

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


def get_post(id=None, slug=None, status=STATUC_PUBLISH):
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
        post['user'] = user_model.get_user(post['user_id'])
        post['categories'] = category_model.get_categories_by_object(post['id'])
        post['tags'] = tag_model.get_tags_by_object(post['id'], 'post')
        return post
    except IndexError:
        return False


def get_posts(page=0, what='*', where=None, vars=None, order=None, total=True, limit=None, offset=None):
    if page > 0:
        limit = limit or 20
        offset = (page-1)*limit

    if order is None:
        order = 'created DESC'

    posts = db.select('posts', what=what, where=where, vars=vars, order=order, limit=limit, offset=offset)

    if total is True:
        total = db.select('posts', what='COUNT(*) AS total', where=where, vars=vars)[0]['total']
    else:
        total = len(posts)

    return posts, total

def get_posts_all(page=0, what='*', where=None, vars=None, order=None, total=True, limit=None, offset=None):
    posts, total = get_posts(page=page, what=what, where=where, vars=vars, order=order, total=total, limit=limit, offset=offset)
    user_ids = []
    ids = []

    posts = list(posts)
    for post in posts:
        ids.append(post.id)
        if post.user_id not in user_ids:
            user_ids.append(post.user_id)

    users = db.select('users', what='id, username', where='id IN $user_ids', vars={'user_ids': user_ids})
    tags = tag_model.get_tags_by_object(ids, 'post')
    categories = category_model.get_categories_by_object(ids)

    users_dict = {}
    tags_dict = {}
    categories_dict = {}
    for user in users:
        users_dict.setdefault(user.id, user)

    for tag in tags:
        tags_dict.setdefault(tag.object_id, [])
        tags_dict[tag.object_id].append(tag)

    for category in categories:
        categories_dict.setdefault(category.object_id, [])
        categories_dict[category.object_id].append(category)

    for post in posts:
        if post.user_id in users_dict:
            post['user'] = users_dict[post.user_id]

        if post.id in tags_dict:
            post['tags'] = tags_dict[post.id]

        if post.id in categories_dict:
            post['categories'] = categories_dict[post.id]

    return posts, total


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
        post_id = db.insert('posts', **values)

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
