from flask import Flask, jsonify, request
from flask.ext.cors import CORS

from bust.web.api_validation import ArgumentValidation, APIValidationError
from bust.web import api_response_creator
from bust import bus_datastore, constants


app = Flask(__name__)
cors = CORS(app) # Enable CORS on all routes
nextbus_datastore = bus_datastore.NextBusDatastoreFactory.generate_datastore()
response_creator = api_response_creator.APIResponseCreator(nextbus_datastore)

@app.route('/api')
def api_root():
    return jsonify(constants.API_HOME_MESSAGE)

@app.route('/api/radius-search')
def radius_search():
    required_args = ['lat', 'lon']
    optional_args = ['distance']
    lat, lon, distance = ArgumentValidation\
        .validate_and_get_float_arg_values(request.args, required_args, optional_args)
    message = response_creator.get_radius_search(lat, lon, distance)
    return jsonify(message)

@app.route('/api/agencies')
def agencies():
    message = response_creator.get_agencies()
    return jsonify(message)

@app.route('/api/agency-routes')
def agency_routes():
    required_args = ['atag']
    agency_tag = ArgumentValidation\
        .validate_and_get_arg_values(request.args, required_args)
    message = response_creator.get_agency_routes(agency_tag)
    return jsonify(message)

@app.route('/api/route-stops')
def route_stops():
    required_args = ['atag', 'rtag']
    agency_tag, route_tag = ArgumentValidation\
        .validate_and_get_arg_values(request.args, required_args)
    message = response_creator.get_route_stops(agency_tag, route_tag)
    return jsonify(message)
        

@app.errorhandler(404)
def not_found(error=None):
    message = {
        'status' : 404,
        'message' : request.url + ' was not found.'
    }
    response = jsonify(message)
    response.status_code = 404
    return response

@app.errorhandler(APIValidationError)
def handle_validation_error(error):
    response = jsonify(error.message_to_dict())
    response.status_code = error.status_code
    return response

def run_app():
	""" Used to hook commandline start """
	app.run()

if __name__ == '__main__':
    app.run()

