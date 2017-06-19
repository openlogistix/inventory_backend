"""
Contains the APIViewSet class and create_api function for the automatic generation
of a RESTful web API.

"""
import json
from collections import OrderedDict

from attachments import handlefiles

from flask import jsonify, request, json
from flask.views import MethodView

class APIViewSet( MethodView ):
    """ Creates a set of views for HTTP requests and routes them to a resource endpoint"""

    def __init__( self, resource, table, db ):
        self.resource   = resource
        self.db         = db
        self.table      = table
        # Primary key is the first column of the table
        self.pri_key    = self.table.keys()[0]

    def get( self, id ):
        """ GET method returns the JSON for the specified resource(s)"""
        if id is None:
            # If no id is given, return the JSON for all records in the database
            try:
                records = self.db.getallmatching(self.resource)
                for record in records:
                    records.append( OrderedDict( zip( self.table.keys(), record ) ) )
                return jsonify( records )
            except Exception as e:
                return 'Unsuccessful. Error:\n' + str(e), 500
        else:
            # Otherwise if there is an ID, return the JSON for the requested record
            try:
                record = self.db.getonematching(self.resource, id=id)
                if not record:
                    return 'Unsuccessful. No resource with ' + self.pri_key + ' %d found.' % id, 404
                return jsonify( OrderedDict( zip( self.table.keys(), record ) ) )
            except Exception as e:
                return 'Unsuccessful. Error:\n' + str(e), 500

    def put( self, id ):
        """ PUT method updates the record with the supplied JSON info """
        try:
            data = OrderedDict( json.loads( request.data ) )
            if self.pri_key in data:
                # Ensure that if the id exists in data, it matches the id provided in URL
                if id != int( data[self.pri_key] ):
                    return 'Error: ID does not match in body and URL', 500
            else:
                # If the id is not in data, add it
                data['id'] = id
            self.db.updateonematching( self.resource, data )
            self.db.commit()
            return 'Successfully updated resource', 201
        except Exception as e:
            return 'Unsuccessful. Error:\n' + str(e), 500

    def delete( self, id ):
        """ DELETE method deletes the record with the matching id """
        self.db.deletematching(self.resource, id=id)
        return 'Successfully deleted resource', 201

    def post( self ):
        """ POST method creates a record with the supplied JSON info """
        try:
            data = OrderedDict( request.get_json() if request.get_json() is not None else request.form)
            self.db.insert(self.resource, **data)
            if request.files:
                id = self.db.getonematching(self.resource, **data)[0]
                # Save any files to disk
                columntofilename = handlefiles(request.files, self.resource, id)
                self.db.updateonematching(self.resource, id=id, **columntofilename)
            return 'Successfully created resource', 201

        except Exception as e:
            raise
            #return 'Unsuccessful. Error:\n' + str(e)


def create_api( server, resource_url, table, db):
    """Create a custom API with standard HTTP methods for GET, POST, PUT, and DELETE """
    # TODO: provide functionality to check if the table exists in the database, and create it
    #       if it has not been made. An optional parameter should exist that enables this feature,
    #       so that the default functionality is not to create tables (in case of typos, etc).

    # Find the resource name from the provided URL
    resource = resource_url.split('/')[-2]
    assert len(resource) > 2, 'Resource URL should be in the form: /path/from/host/to/resource/'

    # Create the views for the API, routing the URLs as needed to the appropriate methods
    resource_views = APIViewSet.as_view( resource + '_api', resource, table, db )
    server.add_url_rule( resource_url, defaults={ 'id':None }, view_func=resource_views, methods=['GET'] )
    server.add_url_rule( resource_url, view_func=resource_views, methods=['POST'] )
    server.add_url_rule( resource_url + '<int:id>', view_func=resource_views, methods=['GET','PUT','DELETE'] )


