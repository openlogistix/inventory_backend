from flask import Flask
from flask import request
import sqlite3
import json
import os

def get_proj_path(path = ""):
    curr_path = os.path.abspath(__file__)
    path_parts = curr_path.split('/')
    curr_path = '/' + '/'.join(path_parts[:-2]) + '/'
    return curr_path + path

def setup():
    pass

def main():
    server = Flask('thingy')

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

        #for key in request.headers:
        #    display_text += '<p>' + key + '   ' + str(headers[key][0])

        conn.close()

        display_text = '<title>Test Page</title>hello?! world?!...<p>' + display_text + '<p>'
        return  display_text + '<p><p>Headers:<p>' + request.headers.__str__().replace('\n','<p>')
    server.run('0.0.0.0',port=7000, debug=True)


setup()
main()
