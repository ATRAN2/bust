from flask import Flask, jsonify, request
from flask.ext.cors import CORS
from bust import api_response_creator, bus_datastore, constants
from bust.api_exceptions import ValidationError

app = Flask(__name__)
cors = CORS(app) # Enable CORS on all routes
nextbus_datastore = bus_datastore.NextBusDatastoreFactory.generate_datastore()
response_creator = api_response_creator.APIResponseCreator(nextbus_datastore)

@app.route('/api')
def api_root():
    message = constants.API_HOME_MESSAGE
    response = jsonify(message)
    response.status_code = 200
    return response

@app.route('/api/radius-search')
def radius_search():
    target_args = ['lat', 'lon']
    _validate_float_args(request.args, target_args)
    lat, lon = _get_arg_values(request.args, target_args)
    lat = float(lat)
    lon = float(lon)
    message = response_creator.get_radius_search(lat, lon)
    response = jsonify(message)
    response.status_code = 200
    return response

@app.route('/api/agencies')
def agencies():
    message = response_creator.get_agencies()
    response = jsonify(message)
    response.status_code = 200
    return response

@app.route('/api/agency-routes')
def agency_routes():
    target_args = ['atag']
    _validate_args(request.args, target_args)
    agency_tag = _get_arg_values(request.args, target_args)
    message = response_creator.get_agency_routes(agency_tag)
    response = jsonify(message)
    response.status_code = 200
    return response

@app.errorhandler(404)
def not_found(error=None):
    message = {
        'status' : 404,
        'message' : request.url + ' was not found.'
    }
    response = jsonify(message)
    response.status_code = 404
    return response

@app.errorhandler(ValidationError)
def handle_validation_error(error):
    response = jsonify(error.message_to_dict())
    response.status_code = error.status_code
    return response

def _validate_float_args(request_args, endpoint_params):
    _validate_args(request_args, endpoint_params)
    try:
        for param in endpoint_params:
            float(request_args[param])
    except (TypeError, ValueError) as e:
        message = 'Bad Request: {0} is not a valid parameter value'.format(e)
        raise ValidationError(message)

def _validate_args(request_args, endpoint_params):
    try:
        for param in endpoint_params:
            request_args[param]
    except KeyError as e:
        message = 'Bad Request: Request does not contain the {0} parameter'.format(e.message)
        raise ValidationError(message)

def _get_arg_values(request_args, target_args):
    if len(target_args) == 1:
        return request_args[target_args[0]]
    arg_values = []
    for target_arg in target_args:
        arg_values.append(request_args[target_arg])
    return arg_values

if __name__ == '__main__':
    app.run()

