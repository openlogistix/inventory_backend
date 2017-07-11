from src import db

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
