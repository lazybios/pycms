import types
import urllib
import re
import web


def get_module_functions(module):
    f = {}
    for var in module.__dict__:
        if isinstance(module.__dict__.get(var), types.FunctionType):
            f[var] = module.__dict__.get(var)
    return f


def ustr(value):
    try:
        return str(value)
    except UnicodeError:
        return unicode(value).encode('UTF-8')

def filter_url(args):
    queries = []
    for arg in args:
        value = web.input().get(arg)
        if value:
            queries.append(arg + '=' + urllib.quote_plus(ustr(value)))
    return '&'.join(queries)

def get_pager_url(base_url, args):
    query = filter_url(args)
    if query:
        query = '?' + query
    return base_url + '/page/%d' + query
