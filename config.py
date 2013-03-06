import web

web.config.debug = True
web.config.email_errors = ''

cache = False

DB_TYPE = 'mysql'
DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASSWORD = '123456'
DB_DATABASE = 'zonday'


db = web.database(dbn=DB_TYPE,
    host=DB_HOST,
    db=DB_DATABASE,
    user=DB_USER,
    pw=DB_PASSWORD)

view_globals = {}
