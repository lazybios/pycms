#encoding=utf-8
import web
from web import form

from admin import render
from app.helpers import validator, session
from app.models import setting as model_setting


setting_form = form.Form(
    form.Textbox('site_name', validator.not_empty, description='站点名称'),
    form.Textbox('site_keyword', description='站点关键字', class_='input-xxlarge'),
    form.Textarea('site_description', description='站点描述', rows='10', cols='20', class_='input-xxlarge'),
    form.Radio('site_status', [('1', '开启'), ('0', '关闭')], value=1, description='站点状态'),
    form.Textarea('site_close_reason', description='站点关闭原因', rows='10', cols='20', class_='input-xxlarge'),
)

class Index:
    def GET(self):
        pass

class Setting:
    def GET(self):
        web.debug(render)
        print(dir(render))
        form = setting_form()
        form.fill(model_setting.get_setting())
        return render.setting(form)

    def POST(self):
        form = setting_form()
        if not form.validates():
            return render.setting(form)

        model_setting.save_setting(form.d)
        session.set_flash('设置保存成功', 'success')
        raise web.seeother('/setting')
