import web
import config

from app.helpers import tags, utils

view_globals = utils.get_module_functions(tags)

render = web.template.render('admin/templates', cache=config.cache, base='layout', globals = view_globals)
