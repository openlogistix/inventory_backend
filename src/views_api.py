"""
Contains the APIViewSet class and create_api function for the automatic generation
of a RESTful web API.

"""
import json
from collections import OrderedDict

from attachments import handlefiles

from flask import jsonify, request, json, current_app
from flask.views import MethodView

class ModelAPI(MethodView):
    def __init__(self, model, db):
        self.model = model
        self.db = db
        self.name = model.__name__.lower()

    def get(self, id):
        instance = self.model.query.get_or_404(id)
        return jsonify(instance.as_dict()), 200

    def put(self, id):
        instance = self.model.query.get_or_404(id)
        data = OrderedDict(json.loads(request.data))
        for k, v in data.iteritems():
            setattr(instance, k, v)
        self.db.session.commit()
        return instance, 201

    def delete(self, id):
        instance = self.model.query.get_or_404(id)
        self.db.session.delete(instance)
        self.db.session.commit()
        return jsonify(instance.as_dict()), 200

    def post(self):
        data = OrderedDict( request.get_json() if request.get_json() is not None else request.form)
        instance = self.model(**data)
        self.db.session.add(instance)
        self.db.session.commit()
        if request.files:
            columntofilename = handlefiles(request.files, self.name, instance.id)
            for col, val in columntofilename.iteritems():
                setattr(instance, col, val)
            self.db.session.commit()
        return jsonify(instance.as_dict()), 201


def create_api( server, resource_url, model, db):
    """Create a custom API with standard HTTP methods for GET, POST, PUT, and DELETE """
    # TODO: provide functionality to check if the table exists in the database, and create it
    #       if it has not been made. An optional parameter should exist that enables this feature,
    #       so that the default functionality is not to create tables (in case of typos, etc).

    # Find the resource name from the provided URL
    resource = resource_url.split('/')[-2]
    assert len(resource) > 2, 'Resource URL should be in the form: /path/from/host/to/resource/'

    # Create the views for the API, routing the URLs as needed to the appropriate methods
    resource_views = ModelAPI.as_view('{model}_api'.format(model=model), model, db)
    server.add_url_rule( resource_url, defaults={ 'id':None }, view_func=resource_views, methods=['GET'] )
    server.add_url_rule( resource_url, view_func=resource_views, methods=['POST'] )
    server.add_url_rule( resource_url + '<int:id>', view_func=resource_views, methods=['GET','PUT','DELETE'] )


