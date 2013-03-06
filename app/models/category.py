#encoding=utf-8
import web

from config import db

_category_settings = {}

def register_model_category(model, **args):
    _category_settings.setdefault(model, {
        'label': model,
        'hierarchical': False,
    })

    _category_settings[model].update(args)

def init_category_settings():
    register_model_category('post', label='文章分类', hierarchical=True)

if not _category_settings:
    init_category_settings()

def get_category_setting(model):
    return _category_settings.get(model)

def get_category_children(model, order=None):
    categories = db.select('categories', where='model=$model', vars={'model': model}, order=order)
    children = {}
    for category in categories:
        if category['parent_id'] in children:
            children[category['parent_id']].append(category)
        else:
            children[category['parent_id']] = [category]
    return children

def get_category_dropdown(model, parent_id=0):
    children = get_category_children(model)
    parents = children.keys()
    depth = -1
    output = []

    def recursive(parent_id, depth):
        if parent_id in parents:
            depth += 1
            for category in children[parent_id]:
                output.append((category['id'], ('-' * depth) + category['name']))
                recursive(category['id'], depth)
    recursive(parent_id, depth)

    return output

def get_category_list(model, parent_id=0):
    children = get_category_children(model)
    parents = children.keys()
    depth = -1
    output = []

    def recursive(parent_id, depth):
        if parent_id in parents:
            depth += 1
            for category in children[parent_id]:
                category['_depth'] = depth
                output.append(category)
                recursive(category['id'], depth)
    recursive(parent_id, depth)
    return output

def get_category(id=None, what='*', where=None, vars=None):
    if id is None and where is None:
        return None

    if id is not None:
        where = 'id=$id'
        vars = {'id': id}

    try:
        return db.select('categories', what=what, where=where, vars=vars, limit=1)[0]
    except IndexError:
        return None

def get_categories_by_object(object_id):
    return db.query('SELECT t1.* FROM categories AS t1 join object_category_relationships AS t2 ON t1.id = t2.category_id WHERE object_id = $object_id', vars={'object_id': object_id})


def new_category(model, name, slug, parent_id=0, description=''):
    category_setting = get_category_setting(model)

    if category_setting is None:
        return False

    if category_setting['hierarchical'] is False:
        parent_id = 0

    parent_id = web.intget(parent_id, 0)

    values = {
        'name': name,
        'slug': slug,
        'parent_id': parent_id,
        'model': model,
        'description': description,
        'count': 0
    }

    return db.insert('categories', **values)

def update_category(model, id=None, where=None, vars=None, **values):
    category_setting = get_category_setting(model)

    if category_setting is None:
        return False

    fields = ['name', 'slug', 'parent_id', 'descrption']
    keys = values.keys()
    for field in keys:
        if field not in fields:
            del values[field]
            continue

        if field == 'parent_id':
            values['parent_id'] = web.intget(values['parent_id'], 0)
            if id is not None and id == values['parent_id'] or category_setting['hierarchical'] is False:
                values['parent_id'] = 0

    if id is not None:
        where = 'id=$id'
        vars = {'id': id}

    return db.update('categories', where=where, vars=vars, **values)

def del_category(ids=None, where=None, vars=None):
    if ids:
        if isinstance(ids, int):
            where = 'id=$id'
            vars = {'id': ids}
        elif isinstance(ids, list):
            if ids:
                where = 'id IN $ids'
                vars = {'ids': ids}
        else:
            return False

    if where is None:
        return False

    t = db.transaction()
    try:
        count = db.delete('categories', where=where, vars=vars)
        db.delete('object_category_relationships', where='category_id IN $ids', vars={'ids': ids})
    except:
        t.rollback()
        return False
    else:
        t.commit()
        return count

def save_category_relationships(object_id, category_ids, new=False):
    if not isinstance(category_ids, list):
        return False

    category_ids = web.uniq(category_ids)

    if not category_ids:
        return False

    t = db.transaction()
    try:
        if new:
            add_category_ids = category_ids
        else:
            old_category_relationships = db.select('object_category_relationships', what='category_id', where='object_id=$object_id', vars={'object_id': object_id})
            old_category_ids = [category['category_id'] for category in old_category_relationships]
            del_category_ids = set(old_category_ids) - set(category_ids)
            add_category_ids = set(category_ids) - set(old_category_ids)

            if del_category_ids:
                db.delete('object_category_relationships', where='object_id=$object_id AND category_id IN $del_category_ids', vars={'object_id': object_id, 'del_category_ids': list(del_category_ids)})

        if add_category_ids:
            db.multiple_insert('object_category_relationships', [{'category_id': category_id, 'object_id': object_id} for category_id in add_category_ids])
    except:
        t.rollback()
        return False
    else:
        t.commit()
        return True
