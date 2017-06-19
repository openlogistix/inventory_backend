import os
import sys
import json
from collections import OrderedDict, namedtuple

import psycopg2
from db import DB
from flask.views import MethodView
from flask import Flask, jsonify, request, json, send_from_directory, render_template

import os

from views_api import create_api

#  _________________________________________________________________________________________
# | Function            | URL                                                               |
# |---------------------+-------------------------------------------------------------------|
# | org admin           | https://openlogistix.io/org/<int:org_id>/                         |
# | list inventory      | https://openlogistix.io/org/<int:org_id>/inventory/               |
# | create/display/edit | https://openlogistix.io/org/<int:org_id>/inventory/<int:obj_id>   |


Item = namedtuple("Item", ["id","org_id", "qr_id", "name", "image", "location", "tags", "description"])
Org =  namedtuple("Org", ["id", "name", "itemlimit"])

class InventoryAPI(Flask):

    def __init__(self, name):
        # Set up Flask server
        Flask.__init__(self, name)

        if 'INVENTORY_SETTINGS' in os.environ:
            self.config.from_envvar('INVENTORY_SETTINGS', silent=True)
        else:
            self.config.from_object('default_config')
        print(self.config)

        db = DB()
        # Define item table column names and data types
        item_cols        = ('id','org_id','qr_id','name','image','location','tags','description')
        item_cols_types  = ('int','int','int','text','text','text','json','text')
        item_table       = OrderedDict( zip( item_cols, item_cols_types ) )

        # Create API for item resource
        create_api( self, '/api/v1/item/',  item_table, db )

        @self.route('/org/<int:org_id>/inventory/<int:qr_id>')
        def inventoryobject(org_id, qr_id):
            """ The landing page from a given QR code. Looks up the given QR id in the db,
                renders it if present, otherwise asks for input. """
            org = Org(*db.getonematching("org", id=org_id))
            result = db.getonematching("item", qr_id=qr_id)
            if result:
                object_data = Item(*result)
                return render_template('objectview.html', item=object_data, org=org), 200
            else:
                return render_template('input.html', qr_id=qr_id, org=org), 200
            return default

        @self.route('/org/<int:org_id>/inventory/')
        def inventory(org_id):
            org = Org(*db.getonematching("org", id=org_id))
            results = db.getallmatching("item", org_id=org_id)
            items = [Item(*row) for row in results]
            return render_template('inventory.html', inventory=items, org=org), 200


debugconfig = {  'host':'0.0.0.0',
            'port':1870,
            'debug':True }

application = InventoryAPI(__name__)
if __name__ == '__main__':
    application.run(**debugconfig)
