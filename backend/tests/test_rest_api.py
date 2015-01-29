import unittest
from bust import main, api_response_creator

class RestAPITest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = main.app.test_client()
        api_response_urls = api_response_creator.APIResponseURLs()
        cls.json_mimetype = 'application/json'
        cls.radius_search_url = api_response_urls.radius_search_url
        cls.agencies_url = api_response_urls.agencies_url
        cls.agency_routes_url= api_response_urls.agency_routes_url

    def test_api_home(self):
        response = self.app.get('/api')
        self.check_response_status_code(response, 200)
        self.check_response_mimetype_is_json(response)
        self.assertIn(self.radius_search_url, response.data)
        self.assertIn(self.agencies_url, response.data)
        self.assertIn(self.agency_routes_url, response.data)

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

    def check_response_mimetype_is_json(self, response):
        self.assertEqual(self.json_mimetype, response.mimetype)

    def check_response_status_code(self, response, status_code):
        self.assertEqual(status_code, response.status_code)

if __name__ == '__main__':
    unittest.main()
