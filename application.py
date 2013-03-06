import web

import config
from admin_application import app as admin_app
from app.helpers import session

urls = (
    '/admin', admin_app
)


app = web.application(urls, globals())
session.init_session(app)

if __name__ == "__main__":
    app.run()
