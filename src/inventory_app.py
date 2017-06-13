import os
import sys
import json
import sqlite3
from collections import OrderedDict, namedtuple

import psycopg2
from flask import Flask, jsonify, request, json, send_from_directory, render_template
from flask.views import MethodView

from views_api import create_api

Gear = namedtuple("Gear", ["id","qr_id", "name", "image", "location", "tags", "description"])

class InventoryAPI(Flask):

    def __init__(self, name):
        # Set up Flask server
        Flask.__init__(self, name)

        # Set up connection to postgres database
        pgconn = self.create_pgconn()
        pgcurs = self.create_pgcurs(pgconn)

        # Define gear table column names and data types
        gear_cols        = ('id','qr_id','name','image','location','weight','width','height','depth','tags')
        gear_cols_types  = ('int','int','text','text','text','int','int','int','int','text')
        gear_table       = OrderedDict( zip( gear_cols, gear_cols_types ) )

        # Create API for gear resource
        create_api( self, '/gear/api/v1/gear/',  gear_table,  pgconn, pgcurs )

        @self.route('/gear/<int:qr_id>')
        def inventoryobject(qr_id):
            """ The landing page from a given QR code. Looks up the given QR id in the db,
                renders it if present, otherwise asks for input. """
            query = "SELECT * FROM gear WHERE qr_id = %s;" 
            pgcurs.execute(query, (qr_id,))
            result = pgcurs.fetchone()
            if result:
                object_data = Gear(*result)
                return render_template('objectview.html', gear=object_data), 200
            else:
                return render_template('input.html', qr_id=qr_id), 200
            return default

        @self.route('/gear/')
        def inventory():
            query = "SELECT *FROM gear;";
            pgcurs.execute(query)
            results = pgcurs.fetchall()
            gearitems = [Gear(*row) for row in results]
            return render_template('inventory.html', geardata=gearitems), 200

    def create_pgconn(self):

        # Initiate a connection to the postgres database
        return psycopg2.connect('dbname=postgres user=postgres')

    def create_pgcurs(self, conn):

        # Create cursor in postgres database
        return conn.cursor()


config = {  'host':'0.0.0.0',
            'port':7000,
            'debug':True }

application = InventoryAPI(__name__)
if __name__ == '__main__':
    application.run(**config)


