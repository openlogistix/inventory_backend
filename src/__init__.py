from flask import Flask
from flask import render_template
from flask_sqlalchemy import SQLAlchemy

import os

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('settings.py')
    app.config.from_envvar('INVENTORY_SETTINGS', silent=True)

    db.init_app(app)

    from models import Item
    from models import Org
    from views_api import create_api
    create_api(app, '/api/v1/item/', models.Item, db)

    @app.route('/org/<int:org_id>/inventory/<int:qr_id>')
    def item(org_id, qr_id):
        org = Org.query.get_or_404(org_id)
        item = Item.query.filter(Item.org_id == org_id, Item.qr_id == qr_id).first()
        if item:
            return render_template('objectview.html', item=item, org=org)
        return render_template('input.html', qr_id=qr_id, org=org)

    @app.route('/org/<int:org_id>/inventory/')
    def inventory(org_id):
        org = Org.query.get_or_404(org_id)
        items = Item.query.all()
        return render_template('inventory.html', inventory=items, org=org), 200

    return app
