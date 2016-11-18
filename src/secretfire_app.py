import os
import sys
import json
import sqlite3
from collections import OrderedDict

import psycopg2
from flask import Flask, jsonify, request, json
from flask.views import MethodView

from views_api import create_api

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
    create_api( server, '/bentest/api/v1/members/',  members_table,  pgconn, pgcurs )

    # Define projects table column names and data types
    projects_cols       = ('id','lead','description','budget')
    projects_cols_types = ('int','int','text','int')
    projects_table      = OrderedDict( zip( projects_cols, projects_cols_types ) )

    # Create API for projects resource
    create_api( server, '/bentest/api/v1/projects/', projects_table, pgconn, pgcurs )

    # Define project_membership table column names and data types
    proj_memb_cols       = ('id','project_id','member_id')
    proj_memb_cols_types = ('int','int','int')
    proj_memb_table      = OrderedDict( zip( proj_memb_cols, proj_memb_cols_types ) )

    # Create API for project_membership resource
    create_api( server, '/bentest/api/v1/project_membership/', proj_memb_table, pgconn, pgcurs )

    @server.route('/bentest')
    def home():

        # Give the headers in the HTTP response
        return '<title>Testing</title>hello?! world?!..<p><p>Headers:<p>' + \
            request.headers.__str__().replace('\n','<p>')

    # Run the server on port 7000
    server.run('0.0.0.0',port=7000, debug=True)

main()
