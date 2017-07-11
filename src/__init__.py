import os

from flask import Flask
from flask import render_template
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_user import login_required, UserManager, SQLAlchemyAdapter

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('settings.py')
    app.config.from_envvar('INVENTORY_SETTINGS', silent=True)

    db.init_app(app)

    from models import Item
    from models import Org
    from models import User
    from views_api import create_api

    db_adapter = SQLAlchemyAdapter(db, User)        # Register the User model
    user_manager = UserManager(db_adapter, app)     # Initialize Flask-User

    create_api(app, '/api/v1/item/', models.Item, db)

    #Routes
    @app.route('/org/<int:org_id>/inventory/<int:qr_id>')
    def item(org_id, qr_id):
        org = Org.query.get_or_404(org_id)
        item = Item.query.filter(Item.org_id == org_id, Item.qr_id == qr_id).first()
        if item:
            return render_template('objectview.html', item=item, org=org)
        return render_template('input.html', qr_id=qr_id, org=org)

    @app.route('/org/<int:org_id>/inventory/')
    @login_required
    def inventory(org_id):
        org = Org.query.get_or_404(org_id)
        items = Item.query.all()
        return render_template('inventory.html', inventory=items, org=org), 200

    @app.before_first_request
    def onetimesetup():
        db.create_all()

    return app
