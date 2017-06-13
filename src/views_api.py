"""
Contains the APIViewSet class and create_api function for the automatic generation
of a RESTful web API.

"""
import os
import os.path
import json
from collections import OrderedDict

from flask import jsonify, request, json
from flask.views import MethodView
# Class APIViewSet creates a set of views for HTTP requests and routes them to a resource endpoint
class APIViewSet( MethodView ):
    
    # Constructor has parameters to define the resource
    def __init__( self, resource, table, connection, cursor ):

        # Store input parameter values into instance member variables
        self.resource   = resource
        self.connection = connection
        self.cursor     = cursor
        self.table      = table

        # Primary key is the first column of the table
        self.pri_key    = self.table.keys()[0]
        
    # GET method will return the JSON for the specified resource(s)
    def get( self, id ):

        # If no id is given, return the JSON for all records in the database
        if id is None:
            try:
                # Perform SQL query for all records
                self.cursor.execute('SELECT * FROM ' + self.resource)
                
                # Create list of dictionaries for JSON output
                records = []
                for record in self.cursor.fetchall():
                    records.append( OrderedDict( zip( self.table.keys(), record ) ) )

                return jsonify( records )
            
            except Exception as e:
                return 'Unsuccessful. Error:\n' + str(e), 500

        # Otherwise if there is an ID, return the JSON for the requested record
        else:
            try:
                # Perform SQL query for a given record
                self.cursor.execute('SELECT * FROM ' + self.resource + ' WHERE ' + \
                    self.pri_key + ' = %s', (str(id),) )
                record = self.cursor.fetchone()

                if not record:
                    return 'Unsuccessful. No resource with ' + self.pri_key + ' %d found.' % id, 404

                return jsonify( OrderedDict( zip( self.table.keys(), record ) ) )

            except Exception as e:
                return 'Unsuccessful. Error:\n' + str(e), 500

    # PUT method will update the record with the supplied JSON info
    def put( self, id ):

        try:
            # Capture HTTP request data (JSON) and load into an update dictionary
            update_dict = OrderedDict( json.loads( request.data ) )

            # Ensure that if the id exists in update_dict, it matches the id provided in URL
            if self.pri_key in update_dict:
                if id != int( update_dict[self.pri_key] ):
                    return 'Error: ID does not match in body and URL', 500
            # If the id is not in update_dict, add it
            else:
                update_dict['id'] = id

            # Execute and commit SQL command
            sql = 'UPDATE ' + self.resource + '\nSET\n' + ',\n'.join([x + ' = %(' + x + ')s' for x in update_dict.keys()]) + '\nWHERE ' + self.pri_key + ' = %(id)s;'
            self.cursor.execute( sql, update_dict )
            self.connection.commit()

            return 'Successfully updated resource with following SQL command:\n' + self.cursor.mogrify( sql, update_dict ), 201

        except Exception as e:
            return 'Unsuccessful. Error:\n' + str(e), 500

    # DELETE method will delete the record with the matching id
    def delete( self, id ):

        # Execute and commit SQL command
        sql = 'DELETE FROM ' + self.resource + ' WHERE id = %s'
        self.cursor.execute(sql, (id,) )
        self.connection.commit()

        return 'Successfully deleted resource', 201

    # POST method will create a record with the supplied JSON info
    def post( self ):
        try:
            insert_dict = OrderedDict( request.get_json() if request.get_json() is not None else request.form)

            # Execute and commit SQL command
            sql ='INSERT INTO ' + self.resource + '\n(' + ', '.join(insert_dict.keys()) + ')\nVALUES\n(' + \
                ', '.join( ['%(' + x + ')s' for x in insert_dict.keys()] )  + ');'
            self.cursor.execute( sql, insert_dict )
            if request.files:
                # Get primary key for last inserted element
                valuegetter = "SELECT currval('{resource}_id_seq');".format(resource=self.resource)
                self.cursor.execute(valuegetter)
                primarykey = self.cursor.fetchone()[0]

                # Save any files to disk
                columntofilename = handlefiles(request.files, self.resource, primarykey)
                sql = "UPDATE {table} SET ".format(table=self.resource) + \
                      ", ".join("{col} = '{val}'".format(col=name, val=filepath) for name, filepath in columntofilename.items()) + \
                      "WHERE id = {key};".format(key=primarykey)
                self.cursor.execute(sql)
            self.connection.commit()
            return 'Successfully created resource with following SQL command:\n' + self.cursor.mogrify( sql, insert_dict ), 201

        except Exception as e:
            raise
            #return 'Unsuccessful. Error:\n' + str(e)

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
STATICFILEPATH = "/var/www/secretfire/static"
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def getext(filename):
    return filename.rsplit(".", 1)[1].lower()

def handlefiles(files, resource, pkey):
    """ Save the files out of a request to a static file directory and returns a dict with a mapping of the files to
        their location on disk. """
    filepaths_dict = {}
    basedir = os.path.join(STATICFILEPATH, resource)
    if not os.path.isdir(basedir):
        os.mkdir(basedir)
    for column, file in files.items():
        ext = getext(file.filename)
        filepath = os.path.join(basedir, "{pkey}_{column}.{ext}".format(pkey=pkey,column=column,ext=ext))
        #Call to the requests file object save() method to save file to disk
        file.save(filepath)
        filepaths_dict[column] = filepath
    return filepaths_dict

# Create a custom API with standard HTTP methods for GET, POST, PUT, and DELETE
def create_api( server, resource_url, table, conn, curs ):
    # TODO: provide functionality to check if the table exists in the database, and create it
    #       if it has not been made. An optional parameter should exist that enables this feature,
    #       so that the default functionality is not to create tables (in case of typos, etc).
    
    # Find the resource name from the provided URL
    resource = resource_url.split('/')[-2]
    assert len(resource) > 2, 'Resource URL should be in the form: /path/from/host/to/resource/'
    
    # Create the views for the API, routing the URLs as needed to the appropriate methods
    resource_views = APIViewSet.as_view( resource + '_api', resource, table, conn, curs )
    server.add_url_rule( resource_url, defaults={ 'id':None }, view_func=resource_views, methods=['GET'] )
    server.add_url_rule( resource_url, view_func=resource_views, methods=['POST'] )
    server.add_url_rule( resource_url + '<int:id>', view_func=resource_views, methods=['GET','PUT','DELETE'] )


