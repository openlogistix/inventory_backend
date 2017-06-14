import os
import sys
import json
from collections import OrderedDict, namedtuple

import psycopg2
from flask.views import MethodView
from flask import Flask, jsonify, request, json, send_from_directory, render_template

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

        # Set up connection to postgres database
        pgconn = self.create_pgconn()
        pgcurs = self.create_pgcurs(pgconn)

        # Define item table column names and data types
        item_cols        = ('id','org_id','qr_id','name','image','location','tags','description')
        item_cols_types  = ('int','int','int','text','text','text','json','text')
        item_table       = OrderedDict( zip( item_cols, item_cols_types ) )

        # Create API for item resource
        create_api( self, '/api/v1/item/',  item_table,  pgconn, pgcurs )

        @self.route('/org/<int:org_id>/inventory/<int:qr_id>')
        def inventoryobject(org_id, qr_id):
            """ The landing page from a given QR code. Looks up the given QR id in the db,
                renders it if present, otherwise asks for input. """
            org = getorg(org_id)
            query = "SELECT * FROM item WHERE qr_id = %s;" 
            pgcurs.execute(query, (qr_id,))
            result = pgcurs.fetchone()
            if result:
                object_data = Item(*result)
                return render_template('objectview.html', item=object_data, org=org), 200
            else:
                return render_template('input.html', qr_id=qr_id, org=org), 200
            return default

        @self.route('/org/<int:org_id>/inventory/')
        def inventory(org_id):
            org = getorg(org_id)
            query = "SELECT * FROM item WHERE org_id = %s;";
            pgcurs.execute(query, (org_id,))
            results = pgcurs.fetchall()
            items = [Item(*row) for row in results]
            return render_template('inventory.html', inventory=items, org=org), 200

        def getorg(id):
            query = "SELECT * FROM org WHERE id = %s;"
            pgcurs.execute(query, (id,))
            result = pgcurs.fetchone()
            org = None
            if result:
                org = Org(*result)
            return org

    def create_pgconn(self):
        db = u = 'openlogistix'
        with open('conf/pw') as pwfile:
            pw = pwfile.read().rstrip()
        # Initiate a connection to the postgres database
        return psycopg2.connect(dbname=db, user=u, password=pw)

    def create_pgcurs(self, conn):

        # Create cursor in postgres database
        return conn.cursor()


debugconfig = {  'host':'0.0.0.0',
            'port':1870,
            'debug':True }

application = InventoryAPI(__name__)
if __name__ == '__main__':
    application.run(**debugconfig)


