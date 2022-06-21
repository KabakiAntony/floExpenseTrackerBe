from flask import Flask
from config import ProductionConfig
from flask_migrate import Migrate
from app.api.view.user import users as users_blueprint
from app.api.view.expense import expenses as expenses_blueprint
from flask_cors import CORS


migrate = Migrate(compare_type=True)


def create_app():
    """ initializing the app factory """
    app = Flask(__name__)
    CORS(app)
    app.config.from_object(ProductionConfig())

    from app.api.model import db, ma

    db.init_app(app)
    ma.init_app(app)
    migrate.init_app(app, db)
    app.register_blueprint(users_blueprint)
    app.register_blueprint(expenses_blueprint)
    app.app_context().push()

    return app
