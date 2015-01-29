from flask import Flask, jsonify, request
from bust import api_response_creator, nextbus_grabber
from werkzeug.contrib.cache import SimpleCache

app = Flask(__name__)
nextbus_datastore = nextbus_grabber.NextbusDatastoreFactory.generate_datastore()
response_creator = api_response_creator.APIResponseCreator(nextbus_datastore)

@app.route('/api')
def api_root():
    api_urls = api_response_creator.APIResponseURLs()
    message = {
        'radius-search' : {
            'url' : api_urls.radius_search_url,
            'action' : 'Searches and returns information about bus stops around <latitude> and <longitude>'},
        'agencies' : {
            'url' : api_urls.agencies_url,
            'action' : 'Returns a list of all California agencies in the Nextbus feed and their agency_tags'},
        'agency_routes': {
            'url' : api_urls.agency_routes_url,
            'action' : 'Returns agency routes and route_tags'}
    }
    response = jsonify(message)
    response.status_code = 200
    return response

@app.route('/api/radius-search')
def radius_search():
    try:
        lat = float(request.args['lat'])
        lon = float(request.args['lon'])
    except (ValueError, TypeError, KeyError):
        message = {'error' : 'Invalid parameters for radius-search'}
        return jsonify(message)
    message = response_creator.create_radius_search(lat, lon)
    if not message:
        message = {'error' : 'No buses found within 50 miles of location'}
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

if __name__ == '__main__':
    app.run(debug = True, use_reloader = False)

