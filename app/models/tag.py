#encoding=utf-8
import urllib
import re
import web

from config import db

def get_tags_by_object(object_id, model):
    if isinstance(object_id, list):
        where = 'object_id IN $object_ids'
        vars = {'object_ids': object_id}
    else:
        where = 'object_id = $object_id'
        vars = {'object_id': object_id}

    where += ' AND model = $model'
    vars['model'] = model

    return db.query('SELECT t1.*, t2.object_id FROM tags AS t1 join object_tag_relationships AS t2 ON t1.id = t2.tag_id WHERE ' + where, vars=vars)

def new_tag(name):
    try:
        return db.select('tags', what='id', where='name=$name', vars={'name': name}, limit=1)[0]['id']
    except IndexError:
        return db.insert('tags', **{'name': name})

def new_tags(tags):
    saved_tags = db.select('tags', what='id, name', where='name IN $tags', vars={'tags': tags})
    tag_ids  = []
    tag_names = []

    for tag in saved_tags:
        tag_ids.append(tag['id'])
        tag_names.append(tag['name'])

    insert_tags = [{'name': tag} for tag in set(tags) - set(tag_names)]
    if not insert_tags:
        return tag_ids

    ids = db.multiple_insert('tags', insert_tags)
    ids = [id + len(insert_tags) - 1 for id in ids] #mysql插入多个last_id为第一行值
    return tag_ids + ids

def save_tag_relationships(object_id, model, tags=None, new=False):
    if isinstance(tags, (unicode, str)):
        tags = tags.split(',')

    if not isinstance(tags, list):
        return False

    tags = [tag.strip() for tag in tags if tag]
    tags = web.uniq(tags)

    if not tags:
        return False

    t = db.transaction()
    try:
        new_tag_ids = new_tags(tags)
        if new:
            add_tag_ids = new_tag_ids
        else:
            old_tag_relationships = db.select('object_tag_relationships', what='tag_id', where='object_id=$object_id AND model=$model', vars={'object_id': object_id, 'model': model})
            old_tag_ids = [tag['tag_id'] for tag in old_tag_relationships]
            del_tag_ids = set(old_tag_ids) - set(new_tag_ids)
            add_tag_ids = set(new_tag_ids) - set(old_tag_ids)

            if del_tag_ids:
                db.delete('object_tag_relationships', where='object_id=$object_id AND model=$model AND tag_id IN $del_tag_ids', vars={'object_id': object_id, 'model': model, 'del_tag_ids': list(del_tag_ids)})

        if add_tag_ids:
            db.multiple_insert('object_tag_relationships', [{'tag_id': tag_id, 'object_id': object_id, 'model': model} for tag_id in add_tag_ids])
    except:
        t.rollback()
        return False
    else:
        t.commit()
        return True
