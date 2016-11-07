from flask import Flask, jsonify, request, json
from collections import OrderedDict
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
    # Set up Flask server
    server = Flask('secret_fire')

    # Set up connection to postgres database
    pgconn = create_pgconn()
    pgcurs = create_pgcurs(pgconn)

    # Define members table column names and data types
    members_cols        = ('id','name','phone_no','email','years','playa_name','location','notes')
    members_cols_types  = ('int','text','text','text','int','text','text','text')
    members_table       = dict( zip( members_cols, members_cols_types ) )

    # Define projects table column names and data types
    projects_cols       = ('id','lead','description','budget')
    projects_cols_types = ('int','int','text','int')
    projects_table      = dict( zip( projects_cols, projects_cols_types ) )

    @server.route('/bentest')
    def home():

        display_text = """
        <title>Test Page</title>
        hello?! world?!...<p>
        """

        return display_text + '<p><p>Headers:<p>' + request.headers.__str__().replace('\n','<p>')

    def check_database_inputs(change_dict, table):
        # TODO: database input sanitation, formatting checks on values

        # Ensure that all columns in change_dict are in the table definition
        for col in change_dict.keys():
            if col not in table.keys():
                return 'Column %s not found in table!' % col

    @server.route('/bentest/api/v1/members/<int:id>', methods = ['GET','PUT','DELETE'])
    def members(id):

        # GET method will return the JSON for the member with that ID
        if request.method == 'GET':
            try:
                pgcurs.execute('SELECT * FROM members WHERE id = %d' % id)
                values = pgcurs.fetchone()

                if not values:
                    return 'Unsuccessful. No member with id %d found.' % id

                return jsonify(OrderedDict(zip(members_cols,values)))

            except Exception as e:
                return 'Unsuccessful. Error:\n' + str(e)

        # PUT method will update the members table with the new, supplied JSON for the member with that ID
        elif request.method == 'PUT':
            try:
                # Capture HTTP request data (JSON) and load into an update dictionary
                update_dict = OrderedDict(json.loads(request.data))

                # Ensure that the id matches
                if id != int(update_dict['id']):
                    return 'Error: ID does not match in body and URL'

                # Perform checks on dict describing values to be updated
                inputs_check = check_database_inputs(update_dict, members_table)
                if inputs_check:
                    return 'Error: ' + output

                # Execute and commit SQL command
                # TODO: incorporate this database sanitzed version into other HTTP methods and into projects HTTP methods
                sql = 'UPDATE members\nSET\n' + ',\n'.join([x + ' = %(' + x + ')s' for x in update_dict.keys()]) + '\nWHERE id = %(id)s;'
                pgcurs.execute( sql, update_dict )
                pgconn.commit()

                return 'Successfully updated member with following SQL command:\n' + sql % update_dict, 201

            except Exception as e:
                return 'Unsuccessful. Error:\n' + str(e)

        # DELETE method will delete a row in the members table at the provided id
        elif request.method == 'DELETE':

            pgcurs.execute('DELETE FROM members WHERE id = %d' % id)

            return 'Successfully deleted member with id %d' % id
        
    @server.route('/bentest/api/v1/members', methods = ['POST'])
    def members_post():

        # POST method will insert a row into the members table of the database with the new, supplied JSON
        try:
            # Capture HTTP request data in JSON
            insert_dict = OrderedDict(json.loads(request.data))

            # Perform checks on dict describing values to be inserted
            inputs_check = check_database_inputs(insert_dict, members_table)
            if inputs_check:
                return 'Error: ' + inputs_check

            # Execute and commit SQL command
            keys = []
            vals = []
            for key in insert_dict:
                keys.append(key)
                vals.append(insert_dict[key])

            # Execute and commit SQL command
            sql ='INSERT INTO members\n(' + ', '.join(insert_dict.keys()) + ')\nVALUES\n(' + ', '.join([str(x) for x in vals])  + ');'
            pgcurs.execute(sql)
            pgconn.commit()

            return 'Successfully created member with following SQL command:\n' + sql, 201

        except Exception as e:
            return 'Unsuccessful. Error:\n' + str(e)

    @server.route('/bentest/api/v1/projects/<int:id>', methods = ['GET','PUT','DELETE'])
    def projects(id):

        # GET method will return the JSON for the project with that ID
        if request.method == 'GET':
            try:
                pgcurs.execute('SELECT * FROM projects WHERE id = %d' % id)
                values = pgcurs.fetchone()

                if not values:
                    return 'Unsuccessful. No project with id %d found.' % id

                return jsonify(OrderedDict(zip(projects_cols,values)))

            except Exception as e:
                return 'Unsuccessful. Error:\n' + str(e)

        # PUT method will update the projects table with the new, supplied JSON for the project with that ID
        elif request.method == 'PUT':
            try:
                # Capture HTTP request data (JSON) and load into an update dictionary
                update_dict = json.loads(request.data)

                # Ensure that the id matches
                if id != int(update_dict['id']):
                    return 'Error: ID does not match in body and URL'

                # Perform checks on dict describing values to be updated
                inputs_check = check_database_inputs(update_dict, projects_table)
                if inputs_check:
                    return 'Error: ' + inputs_check

                # Execute and commit SQL command
                sql = 'UPDATE projects\nSET\n' + ',\n'.join([x + ' = ' + str(update_dict[x]) for x in update_dict.keys()]) + '\nWHERE id = %d;' % id
                pgcurs.execute(sql)
                pgconn.commit()

                return 'Successfully updated project with id %d' % id + ' with following SQL command:\n' + sql, 201

            except Exception as e:
                return 'Unsuccessful. Error:\n' + str(e)

        # DELETE method will delete a row in the projects table at the provided id
        elif request.method == 'DELETE':

            pgcurs.execute('DELETE FROM projects WHERE id = %d' % id)

            return 'Successfully deleted projects with id %d' % id

    @server.route('/bentest/api/v1/projects', methods = ['POST'])
    def projects_post():

        # POST method will insert a row into the projects table of the database with the new, supplied JSON
        try:
            # Capture HTTP request data in JSON
            insert_dict = json.loads(request.data)

            # Perform checks on dict describing values to be inserted
            inputs_check = check_database_inputs(insert_dict, projects_table)
            if inputs_check:
                return 'Error: ' + inputs_check

            # Execute and commit SQL command
            keys = []
            vals = []
            for key in insert_dict.keys():
                keys.append(key)
                vals.append(insert_dict[key])

            # Execute and commit SQL command
            sql ='INSERT INTO projects\n(' + ', '.join(keys) + ')\nVALUES\n(' + ', '.join([str(x) for x in vals])  + ');'
            pgcurs.execute(sql)
            pgconn.commit()

            return 'Successfully created project with following SQL command:\n' + sql, 201

        except Exception as e:
            return 'Unsuccessful. Error:\n' + str(e)

    # TODO: modify to be useful
    import view_test
    view_test.run_view_test(server)

    # Run the server on port 7000
    server.run('0.0.0.0',port=7000, debug=True)

main()

