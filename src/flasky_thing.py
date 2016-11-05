from flask import Flask, jsonify, request, json
import psycopg2
import sqlite3
import json
import sys
import os

def get_proj_path(path = ''):
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

    members_cols = ('id','name','phone_no','email','years','playa_name','location','notes')
    members_cols_types = ('int','text','text','text','int','text','text','text')

    @server.route('/bentest')
    def home():
        # load sqlite3 database
        conn = sqlite3.connect(get_proj_path('data/') + 'testdb.db')
        cursor = conn.cursor()
        
        cursor.execute('INSERT INTO requests (method, number, notes)\n VALUES (' +
            ','.join( ['\'' + request.method + '\'', str(0), '\'notenote\'' ] ) + ');')
        conn.commit()

        display_text = ''
        display_text += '<p>database contents:'
        for row in cursor.execute('SELECT * FROM requests'):
            display_text += '<p>' + '\t'.join([str(x) for x in row])
            pass

        conn.close()

        display_text = '<title>Test Page</title>hello?! world?!...<p>' + display_text + '<p>'

        return  display_text + '<p><p>Headers:<p>' + request.headers.__str__().replace('\n','<p>')

    @server.route('/bentest/api/v1/members/<int:id>', methods=['GET','POST','PUT','DELETE'])
    def members(id):

        # GET method will return the JSON for the member with that ID
        if request.method == 'GET':
            pgcurs.execute('SELECT * FROM members WHERE id = %d' % id)
            values = pgcurs.fetchone()
            #return jsonify(dict(zip(members_cols,values)))
            return jsonify(values)

        # POST method will update the database with the new, supplied JSON for the member with that ID
        elif request.method == 'POST':
            try:
                # Capture HTTP request data in JSON
                values = json.loads(request.data)

                # Ensure that the id matches
                if id != int(values[0]):
                    return 'ERROR: ID does not match in body and URL'

                # TODO: database input sanitation, formatting checks on values
                
                # Format the values so that they can be pasted into the SQL UPDATE command
                for i, x in enumerate(values):
                    if values[i]:
                        if members_cols_types[i] == 'text':
                                values[i] = '\'' + values[i] + '\''
                    else:
                        values[i] = 'null'

                # Create dict for the SQL UPDATE command with column name, values as key, value pairs
                update_dict = dict(zip(members_cols[1:],values[1:])) 

                # Execute and commit SQL command
                sql ='UPDATE members\nSET\n' + ',\n'.join([x + ' = ' + str(update_dict[x]) for x in update_dict.keys()]) + '\nWHERE id = %d;' % id
                pgcurs.execute(sql)
                pgconn.commit()

                return 'Successfully updated member with id %d' % id + ' with following SQL command:\n' + sql

            except Exception as e:
                return 'Unsuccessful. Error:\n' + str(e)

        elif request.method == 'PUT':
            try:
                # Capture HTTP request data in JSON
                values = json.loads(request.data)

                # Ensure that the id matches TODO: what index should be used in URL?
                #if id != int(values[0]):
                #   return 'ERROR: ID does not match in body and URL'

                # TODO: database input sanitation, formatting checks on values
                
                # Format the values so that they can be pasted into the SQL INSERT command
                for i, x in enumerate(values):
                    if values[i]:
                        if members_cols_types[i] == 'text':
                            values[i] = '\'' + values[i] + '\''
                    else:
                        values[i] = 'null'

                # Execute and commit SQL command
                sql ='INSERT INTO members\n(' + ', '.join(members_cols[1:]) + ')\nVALUES\n(' + ', '.join([str(x) for x in values[1:]])  + ');'
                pgcurs.execute(sql)
                pgconn.commit()

                return 'Successfully created member with following SQL command:\n' + sql

            except Exception as e:
                return 'Unsuccessful. Error:\n' + str(e)

        elif request.method == 'DELETE':
            pgcurs.execute('DELETE FROM members WHERE id = %d' % id)
            return 'Successfully deleted member with id %d' % id
    


    server.run('0.0.0.0',port=7000, debug=True)

main()
