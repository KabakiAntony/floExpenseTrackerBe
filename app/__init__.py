from flask import Flask
from config import ProductionConfig
from flask_migrate import Migrate
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
    # register blueprints here
    app.app_context().push()

    return app