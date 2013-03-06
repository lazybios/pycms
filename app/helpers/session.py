import web

def init_session(app):
    session = web.session.Session(app, web.session.DiskStore('sessions'), initializer={'is_logged' : False})
    def session_hook():
        web.ctx.session = session
    app.add_processor(web.loadhook(session_hook))

def get_session():
    return web.ctx.session

def is_logged():
    return get_session().is_logged

def login():
    pass

def logout():
    get_session().kill()

def login_required(method):
    def wrap(*args, **kwargs):
        if not is_logged():
            return web.found('/login', True)
        else:
            return method(*args, **kwargs)
    return wrap

def set_flash(message, t='note'):
    session = get_session()
    if session.get('flash') is None:
        session.flash = {}
    session.flash.update({t: message})

def get_flash(t='note'):
    session = get_session()
    message = ''
    if not session.get('flash') is None:
        flash = session.get('flash')
        if not flash.get(t) is None:
            message = flash[t]
            del flash[t]
    return message
