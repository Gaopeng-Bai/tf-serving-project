"""
coding: utf-8
python: 3.7.6
Date: 2021-04-03 11:48:44
@Software: VsCode
@Author: Gaopeng Bai
@Email: gaopengbai0121@gmail.com
@Description:
"""
import unittest

import sys
sys.path.append('../flask_server')
from app import app


class TestAPI(unittest.TestCase):

    def setUp(self):
        # config test_client
        app.config['TESTING'] = True
        self.app = app.test_client()

    def tearDown(self):
        pass

    def test_hello_world(self):
        # test /
        rv = self.app.get('/')
        data = rv.get_json()
        self.assertEqual(rv.status_code, 200)
        self.assertIsInstance(data, dict)
        self.assertEqual(data["retcode"], 200)
        self.assertEqual(data["retmsg"], 'Hello World!')

    def test_check_health(self):
        # test /health
        rv = self.app.get('/health')
        data = rv.get_json()
        self.assertEqual(rv.status_code, 200)
        self.assertIsInstance(data, dict)
        self.assertEqual(data["retcode"], 200)
        self.assertEqual(data["retmsg"], 'Healthy!')

    def test_not_found_error_handler(self):
        # we test this error handler by using a not defined api
        rv = self.app.get('/not_defined')
        data = rv.get_json()
        self.assertEqual(rv.status_code, 404)
        self.assertIsInstance(data, dict)
        self.assertEqual(data["retcode"], 404)
        self.assertIn("404 Not Found", data['retmsg'])

    def test_method_not_allowed_handler(self):
        # we test this error handler by posting to '/health' api which is supposed to be a GET api
        rv = self.app.post('/health')
        data = rv.get_json()
        self.assertEqual(rv.status_code, 405)
        self.assertIsInstance(data, dict)
        self.assertEqual(data["retcode"], 405)
        self.assertIn("405 Method Not Allowed", data['retmsg'])

    def test_bad_request_error_handler(self):
        # we test this error handler by posting None to '/predict' api which is supposed to be posted with
        # application/json data
        rv = self.app.post('/predict', data=None)
        data = rv.get_json()
        self.assertEqual(rv.status_code, 400)
        self.assertIsInstance(data, dict)
        self.assertEqual(data["retcode"], 400)
        self.assertIn("400 Bad Request", data['retmsg'])
