#encoding=utf-8

from web import form
from config import db

not_empty = form.Validator('不能为空', lambda value: bool(value.strip()))

email = form.regexp(r"(^[-!#$%&'*+/=?^_`{}|~0-9A-z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-z]+)*"  # dot-atom
    # quoted-string, see also http://tools.ietf.org/html/rfc2822#section-3.2.5
    r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-\011\013\014\016-\177])*"'
    r')@((?:[A-z0-9](?:[A-z0-9-]{0,61}[A-z0-9])?\.)+[A-z]{2,6}\.?$)'  # domain
    r'|\[(25[0-5]|2[0-4]\d|[0-1]?\d?\d)(\.(25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3}\]$', '必须是有效的电子邮件地址')

alpha_numeric = form.regexp(r'^[A-z0-9]+$', '必须只包含数字和英文字符')

slug = form.regexp(r'^[A-z0-9\-]+$', '必须只包含英文和数字、-')


def max_length(max_num):
    return form.Validator('长度必须小于等于%d' % max_num, lambda value: len(value) <= max_num)


def min_length(min_num):
    return form.Validator('长度必须大于等于%d' % min_num, lambda value: len(value) >= min_num)


def between(min_num, max_num):
    return form.Validator('长度必须在%d和%d之间' % (min_num, max_num), lambda value: (len(value) >= min_num) and (len(value) <= max_num))


def match(match_value):
    return form.Validator('不匹配', lambda value: match_value == value)


def unique(table, field, where=None, vars=None):
    def is_unique(field, value, where=None, vars=None):
        if not where is None:
            where = where + ' AND ' + field + '=$' + field
            if vars is None:
                vars = {}
            vars.update({field: value})
        else:
            where = field + '=$' + field
            vars = {field: value}

        try:
            db.select(table, what='id', where=where, vars=vars, limit=1)[0]
            return False
        except IndexError:
            return True
    return form.Validator('不是唯一的', lambda value: is_unique(field, value, where, vars))
