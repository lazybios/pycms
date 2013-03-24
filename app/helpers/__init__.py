import web
import config

from app.helpers import tags, utils
from app.models import setting

setting.update_view_site_setting()
view_globals = utils.get_module_functions(tags)
view_globals.update(config.view_globals)


def get_render(name, layout='layout'):
    return web.template.render(
        '%s/templates' % name,
        cache=config.cache,
        base=layout,
        globals=view_globals)
