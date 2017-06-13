import os
import sys
import json
import sqlite3
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

class InventoryAPI(Flask):

    def __init__(self, name):
        # Set up Flask server
        Flask.__init__(self, name)

        # Set up connection to postgres database
        pgconn = self.create_pgconn()
        pgcurs = self.create_pgcurs(pgconn)

        # Define item table column names and data types
        item_cols        = ('id','org_id','qr_id','name','image','location','weight','width','height','depth','tags')
        item_cols_types  = ('int','int','int','text','text','text','int','int','int','int','text')
        item_table       = OrderedDict( zip( item_cols, item_cols_types ) )

        # Create API for item resource
        create_api( self, '/api/v1/item/',  item_table,  pgconn, pgcurs )

        @self.route('/org/<int:org_id>/inventory/<int:qr_id>')
        def inventoryobject(qr_id):
            """ The landing page from a given QR code. Looks up the given QR id in the db,
                renders it if present, otherwise asks for input. """
            query = "SELECT * FROM item WHERE qr_id = %s;" 
            pgcurs.execute(query, (qr_id,))
            result = pgcurs.fetchone()
            if result:
                object_data = Item(*result)
                return render_template('objectview.html', item=object_data), 200
            else:
                return render_template('input.html', qr_id=qr_id), 200
            return default

        @self.route('/org/<int:org_id>/inventory/')
        def inventory():
            query = "SELECT * FROM items WHERE org_id = %s;";
            pgcurs.execute(query, (org_id,))
            results = pgcurs.fetchall()
            items = [Item(*row) for row in results]
            return render_template('inventory.html', inventory=items), 200

    def create_pgconn(self):

        # Initiate a connection to the postgres database
        return psycopg2.connect('dbname=openlogistix user=openlogistix')

    def create_pgcurs(self, conn):

        # Create cursor in postgres database
        return conn.cursor()


config = {  'host':'0.0.0.0',
            'port':7000,
            'debug':True }

application = InventoryAPI(__name__)
if __name__ == '__main__':
    application.run(**config)


