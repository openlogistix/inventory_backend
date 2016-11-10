from flask import Flask, jsonify, request, json
from flask.views import MethodView
from collections import OrderedDict
from views_api import create_API
import psycopg2
import sqlite3
import json
import sys
import os

def create_pgconn():

    # Initiate a connection to the postgres database
    return psycopg2.connect('dbname=postgres user=postgres')

def create_pgcurs(conn):

    # Create cursor in postgres database
    return conn.cursor()

def main():

    # Set up Flask server
    server = Flask('secret_fire')

    # Set up connection to postgres database
    pgconn = create_pgconn()
    pgcurs = create_pgcurs(pgconn)

    # Define members table column names and data types
    members_cols        = ('id','name','phone_no','email','years','playa_name','location','notes')
    members_cols_types  = ('int','text','text','text','int','text','text','text')
    members_table       = OrderedDict( zip( members_cols, members_cols_types ) )

    # Create API for members resource
    create_API( server, '/bentest/api/v1/members/',  members_table,  pgconn, pgcurs )

    # Define projects table column names and data types
    projects_cols       = ('id','lead','description','budget')
    projects_cols_types = ('int','int','text','int')
    projects_table      = OrderedDict( zip( projects_cols, projects_cols_types ) )

    # Create API for projects resource
    create_API( server, '/bentest/api/v1/projects/', projects_table, pgconn, pgcurs )

    @server.route('/bentest')
    def home():

        # Create test page for /bentest
        display_text = """
        <title>Test Page</title>
        hello?! world?!...<p>
        """

        # Give the headers in the HTTP response
        return display_text + '<p><p>Headers:<p>' + request.headers.__str__().replace('\n','<p>')

    # Run the server on port 7000
    server.run('0.0.0.0',port=7000, debug=True)

main()

