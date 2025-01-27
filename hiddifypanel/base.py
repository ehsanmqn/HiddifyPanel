import flask_bootstrap
import hiddifypanel
from dynaconf import FlaskDynaconf
from flask import Flask, request, g
from flask_babelex import Babel
from hiddifypanel.panel.init_db import init_db


def create_app(**config):
    app = Flask(__name__, static_url_path="/<proxy_path>/static/", instance_relative_config=True)
    FlaskDynaconf(app)
    app.jinja_env.line_statement_prefix = '%'
    flask_bootstrap.Bootstrap4(app)
    hiddifypanel.panel.database.init_app(app)

    with app.app_context():
        init_db()

    hiddifypanel.panel.common.init_app(app)
    hiddifypanel.panel.admin.init_app(app)
    hiddifypanel.panel.user.init_app(app)
    hiddifypanel.panel.cli.init_app(app)
    hiddifypanel.panel.restapi.init_app(app)

    app.config.update(config)  # Override with passed config
    app.config['WTF_CSRF_CHECK_DEFAULT'] = False

    babel = Babel(app)

    @babel.localeselector
    def get_locale():
        # Put your logic here. Application can store locale in
        # user profile, cookie, session, etc.
        from hiddifypanel.models import ConfigEnum, hconfig
        if "admin" in request.base_url:
            g.locale = hconfig(ConfigEnum.admin_lang) or hconfig(ConfigEnum.lang) or 'fa'
        else:
            g.locale = hconfig(ConfigEnum.lang) or "fa"
        return g.locale

    from flask_wtf.csrf import CSRFProtect

    csrf = CSRFProtect(app)

    @app.before_request
    def check_csrf():
        if "/admin/user/" in request.base_url: return
        if "/admin/domain/" in request.base_url: return
        if "/admin/actions/" in request.base_url: return
        if "/api/v1/" in request.base_url: return
        csrf.protect()

    app.jinja_env.globals['get_locale'] = get_locale
    app.jinja_env.globals['version'] = hiddifypanel.__version__

    return app


def create_app_wsgi():
    # workaround for Flask issue
    # that doesn't allow **config
    # to be passed to create_app
    # https://github.com/pallets/flask/issues/4170
    app = create_app()
    return app
