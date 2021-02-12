from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_dance.consumer.storage.sqla import OAuthConsumerMixin
from flask_dance.consumer.storage.sqla import SQLAlchemyStorage
import os
from sqlalchemy_utils.types.json import JSONType

db = SQLAlchemy()

database_path = os.environ.get('DATABASE_URL')


def setup_db(app, blueprint, database_path=database_path):
    app.config['SQLALCHEMY_DATABASE_URI'] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    migrate = Migrate(app, db)
    print(blueprint)
    blueprint.storage = SQLAlchemyStorage(OAuth, db.session)


class OAuth(OAuthConsumerMixin, db.Model):
    pass