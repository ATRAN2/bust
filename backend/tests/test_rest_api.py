import unittest
from bust import main, constants

class RestAPITest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = main.app.test_client()
        cls.json_mimetype = 'application/json'

    def test_api_home(self):
        response = self.app.get('/api')
        self.check_response_status_code(response, 200)
        self.check_response_mimetype_is_json(response)
        self.assertIn(constants.RADIUS_SEARCH_URL, response.data)
        self.assertIn(constants.AGENCIES_URL, response.data)
        self.assertIn(constants.AGENCY_ROUTES_URL, response.data)

    def test_404_page(self):
        response = self.app.get('/not_a_page')
        self.assertIn('"status": 404', response.data)
        self.check_response_status_code(response, 404)
        self.check_response_mimetype_is_json(response)

    def test_radius_search(self):
        response = self.app.get('/api/radius-search?lat=37.8721999&lon=-122.2687799')
        self.assertIn('University Av & Shattuck Av', response.data)
        self.check_response_status_code(response, 200)
        self.check_response_mimetype_is_json(response)

    def test_agencies(self):
        response = self.app.get('/api/agencies')
        self.assertIn('actransit', response.data)
        self.check_response_status_code(response, 200)
        self.check_response_mimetype_is_json(response)

    def test_agency_routes(self):
        response = self.app.get('/api/agency-routes?atag=actransit')
        self.assertIn('51B', response.data)
        self.check_response_status_code(response, 200)
        self.check_response_mimetype_is_json(response)

    def test_validation_error_handler(self):
        response = self.app.get('/api/radius-search?lat=notanumber&lon=notanumber')
        self.assertIn('notanumber is not a valid parameter value', response.data)
        response = self.app.get('/api/radius-search?lat=37.8721999')
        self.assertIn('Request does not contain the lon parameter', response.data)

    def check_response_mimetype_is_json(self, response):
        self.assertEqual(self.json_mimetype, response.mimetype)

    def check_response_status_code(self, response, status_code):
        self.assertEqual(status_code, response.status_code)

if __name__ == '__main__':
    unittest.main()
