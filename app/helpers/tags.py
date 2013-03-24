#encoding=utf-8

import math

from app.helpers import utils, session


def input_error_class(note):
    if not note is None:
        return ' error'


def get_flash(tp='all'):
    s = session.get_session()
    alerts = []
    if not s.get('flash') is None:
        keys = s.get('flash').keys()
        alerts = ['<div class="alert alert-%s">%s</div>' % (t, session.get_flash(t)) for t in keys if tp == 'all' or t == tp]

    return ''.join(alerts)


def pagination(current_page=1, total=0, per_num=20, max_pager_links = 8, base_url= '', base_args=[], class_=''):
    if total == 0 or per_num == 0:
        return ''

    max_pager_links = 8
    num_pages = int(math.ceil(total * 1.0 / per_num))

    if num_pages == 1:
        return ''

    if num_pages <= max_pager_links:
        start = 0
        end = num_pages
    else:
        start = max(int(math.floor(current_page - max_pager_links / 2)), 0)
        if start > (num_pages - max_pager_links):
            start = num_pages - max_pager_links
        end = min(start + max_pager_links, num_pages)

    pages = [page for page in range(start + 1, end + 1)]
    frist_page = last_page = next_page = prev_page = False

    if current_page > 1:
        first_page = 1

    if current_page < num_pages:
        last_page = num_pages

    if current_page > 1:
        prev_page = current_page - 1

    if current_page < num_pages:
        next_page = current_page + 1

    output = []
    pager_url = utils.get_pager_url(base_url, base_args)

    if prev_page:
        output.append(u'<li><a href="%s">上一页</a></li>' % (pager_url % prev_page))
    else:
        output.append(u'<li class="disabled"><span>上一页</span></li>')

    for page in pages:
        if page == current_page:
            output.append('<li class="active"><span>%d</span>' % page)
        else:
            output.append('<li><a href="%s">%d</a></li>' % ((pager_url % page), page))

    if next_page:
        output.append(u'<li><a href="%s">下一页</a></li>' % (pager_url % next_page))
    else:
        output.append(u'<li class="disabled"><span>下一页</span></li>')

    return ('<div class="pagination %s">' % class_) + '\n<ul>\n' + '\n'.join(output) + '\n</ul>\n</div>'
