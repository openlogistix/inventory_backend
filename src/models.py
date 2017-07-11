from src import db
from flask_user import UserMixin

class ModelMixin(object):
    def as_dict(self):
        return {col.name: getattr(self, col.name) for col in self.__table__.columns}

class Item(db.Model, ModelMixin):
    __tablename__ = 'item'
    id = db.Column(db.Integer, primary_key=True)

    # TODO: make this actually a foreign key
    org_id = db.Column(db.Integer)

    qr_id = db.Column(db.Integer, unique=True)

    # TODO: use db.Unicode??
    name = db.Column(db.String)
    image = db.Column(db.String)
    location = db.Column(db.String)
    tags = db.Column(db.JSON)
    description = db.Column(db.String)

class Org(db.Model, ModelMixin):
    __tablename__ = 'org'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    itemlimit = db.Column(db.Integer)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)

    # User authentication information
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False, server_default='')

    # User email information
    email = db.Column(db.String(255), nullable=False, unique=True)
    confirmed_at = db.Column(db.DateTime())

    # User information
    active = db.Column('is_active', db.Boolean(), nullable=False, server_default='0')
    first_name = db.Column(db.String(100), nullable=False, server_default='')
    last_name = db.Column(db.String(100), nullable=False, server_default='')


