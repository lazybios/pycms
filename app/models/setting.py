#encoding=utf-8
import web

from config import db, view_globals

_setting = {}
_keys = ['site_name',
        'site_keyword',
        'site_description',
        'site_status',
        'site_close_reason',]

def save_setting(data):
    setting = get_setting()
    keys = setting.keys()
    rows = []

    for key, value in data.iteritems():
        if key in keys and value != setting[key]:
            rows.append({'key': key, 'value': value})
            setting[key] = value

    if rows:
        for row in rows:
            where = '`key`=$key'
            vars = {'key': row['key']}
            db.update('settings', where=where, vars=vars, **{'value': row['value']})

    update_view_site_setting()
    return True

def get_setting(key=None):
    if not _setting:
        result = db.select('settings')

        for row in result:
            _setting[row.key] = row.value

        keys = _setting.keys()
        insert_keys = set(_keys) - set(keys)
        values = []

        for key in insert_keys:
            values.append({'`key`': key, 'value': ''})
            _setting[key] = ''

        if values:
            db.multiple_insert('settings', values)

    if key is None:
        return _setting
    else:
        _setting.get(key)

def update_view_site_setting():
    if view_globals.get('site') is None:
        view_globals['site'] = {}

    setting = get_setting()
    view_globals['site']['name'] = setting['site_name']
    view_globals['site']['keyword'] = setting['site_keyword']
    view_globals['site']['description'] = setting['site_description']


