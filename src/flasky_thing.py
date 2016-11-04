from flask import Flask, jsonify, request
import psycopg2
import sqlite3
import json
import os

def get_proj_path(path = ""):
    curr_path = os.path.abspath(__file__)
    path_parts = curr_path.split('/')
    curr_path = '/' + '/'.join(path_parts[:-2]) + '/'
    return curr_path + path

def create_pgconn():

    # Initiate a connection to the postgres database
    return psycopg2.connect('dbname=postgres user=postgres')

def create_pgcurs(conn):

    # Create cursor in postgres database
    return conn.cursor()

def main():
    server = Flask('thingy')

    pgconn = create_pgconn()
    pgcurs = create_pgcurs(pgconn)

    @server.route('/bentest')
    def home():
        # load sqlite3 database
        conn = sqlite3.connect(get_proj_path('data/') + 'testdb.db')
        cursor = conn.cursor()
        
        cursor.execute('INSERT INTO requests (method, number, notes)\n VALUES (' +
            ','.join( ['\'' + request.method + '\'', str(0), '\'notenote\'' ] ) + ');')
        conn.commit()

        display_text = ""
        display_text += "<p>database contents:"
        for row in cursor.execute('SELECT * FROM requests'):
            display_text += '<p>' + '\t'.join([str(x) for x in row])
            pass

        conn.close()

        display_text = '<title>Test Page</title>hello?! world?!...<p>' + display_text + '<p>'

        return  display_text + '<p><p>Headers:<p>' + request.headers.__str__().replace('\n','<p>')

    @server.route('/bentest/api/v1/members/<int:id>', methods=['GET','POST','PUT','DELETE'])
    def members(id):

        if request.method == 'GET':
            pgcurs.execute("SELECT * FROM members WHERE id = %d" % id)
            return jsonify(pgcurs.fetchone())

        elif request.method == 'POST':
            pass
        elif request.method == 'PUT':
            pass
        elif request.method == 'DELETE':
            pass
    


    server.run('0.0.0.0',port=7000, debug=True)

main()
