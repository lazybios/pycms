#encoding=utf-8

import web
from md5 import md5
from datetime import datetime

from config import db

ROOT_ID = 1

ROLE_ROOT = 10
ROLE_GUEST = 0

roles = {
    ROLE_ROOT: '超级管理员',
    ROLE_GUEST: '游客',
}

STATUS_ACTIVATED = 1
STATUS_NOT_ACTIVATED = 0
STATUS_DISABLED = 2

status_list = {
    STATUS_NOT_ACTIVATED: '未激活',
    STATUS_ACTIVATED: '已激活',
    STATUS_DISABLED: '已禁用',
}

def login(username, password):
    where = 'username=$username AND password=$password'
    vars = {'username': username, 'password': md5(password).hexdigest()}
    try:
        user = db.select('users', what='id, username, last_login', where=where, vars=vars, limit=1)[0]
        db.update('users', where=user['id'], **{'last_login': datetime.utcnow()})
        return user
    except IndexError:
        return False;

def get_user(id=None, what='*', where=None, vars=None):
    if isinstance(id, int):
        where = 'id=$id'
        vars = {'id': id}

    if where is None:
        return None

    try :
        return db.select('users', what=what, where=where, vars=vars, limit=1)[0]
    except IndexError:
        return None

def get_users(page=0, what='*', where=None, vars=None, order=None, total=True, limit=None, offset=None):
    if page > 0:
        limit = limit or 20
        offset = (page-1)*limit

    if order is None:
        order = 'created DESC'

    users = db.select('users', what=what, where=where, vars=vars, order=order, limit=limit, offset=offset)
    if total is True:
        total = db.select('users', what='COUNT(*) AS total', where=where, vars=vars)[0]['total']
    else:
        total = len(users)

    return users, total

def new_user(username, password, email, role=ROLE_GUEST, status=STATUS_NOT_ACTIVATED):
    if not status in status_list.keys():
        status = STATUS_NOT_ACTIVATED

    values = {
        'username': username,
        'password': md5(password).hexdigest(),
        'email': email,
        'role': role,
        'status': status,
        'created': datetime.utcnow(),
        'modified': datetime.utcnow(),
    }
    return db.insert('users', **values)

def update_user(id=None, where=None, vars=None, **values):
    fields = ['username', 'password', 'email', 'status', 'role', 'last_login', 'activation_key'];
    for field in values.keys():
        if not field in fields:
            del values[field]
            continue

        if field == 'password':
            values[field] = md5(values[field]).hexdigest()

        if field == 'status' and int(values[field]) == STATUS_ACTIVATED:
            values.update({'activation_key': ''})

        if field == 'status':
            if not values[field] in status_list.keys():
                values[field] = STATUS_NOT_ACTIVATED

    values.update({'modified': datetime.utcnow()})

    if id is not None:
        where = 'id=$id'
        vars = {'id': id}

    return db.update('users', where=where, vars=vars, **values)

def del_user(ids=None, where=None, vars=None):
    if ids:
        if isinstance(ids, int) and ids != ROOT_ID:
            where = 'id=$id'
            vars = {'id': ids}
        elif isinstance(ids, list):
            if ROOT_ID in ids:
                ids.remove(ROOT_ID)

            if ids:
                where = 'id IN $ids'
                vars = {'ids': ids}
        else:
            return False

    if where is None:
        return False

    return db.delete('users', where=where, vars=vars)
