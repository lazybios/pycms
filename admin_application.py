import web
from app.helpers import session

urls = (
    '/post', 'admin.controllers.post.Index',
    '/post/add', 'admin.controllers.post.Add',
    '/post/edit/(\d+)', 'admin.controllers.post.Edit',
    '/post/delete/(\d+)', 'admin.controllers.post.Delete',

    '/([a-z]+)/category', 'admin.controllers.category.Index',
    '/([a-z]+)/category/add', 'admin.controllers.category.Add',
    '/([a-z]+)/category/edit/(\d+)', 'admin.controllers.category.Edit',

    '/user', 'admin.controllers.user.Index',
    '/user/profile', 'admin.controllers.user.Profile',
    '/user/page/(\d+)', 'admin.controllers.user.Index',
    '/user/add', 'admin.controllers.user.Add',
    '/user/edit/(\d+)', 'admin.controllers.user.Edit',

    '/setting', 'admin.controllers.site.Setting',
)

def admin_processor(handler):
    return handler()
    #return session.login_required(handler)()

app = web.application(urls, globals())
app.add_processor(admin_processor)
