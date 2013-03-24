import web

from admin_application import app as admin_app
from app.helpers import session

urls = (
    '/login', 'app.controllers.site.Login',
    '/logout', 'app.controllers.site.Logout',
    '/admin', admin_app
)

app = web.application(urls, globals())
session.init_session(app)

if __name__ == "__main__":
    app.run()
