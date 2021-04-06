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
import json
import os

import sys
sys.path.append('../flask_server')
from app import app


# Assume you have started TF-serving on http://localhost:8501 with 'dnn_model/001' served
# docker run --rm -p 8501:8501 tf_serving:1.0
class TestIntegration(unittest.TestCase):

    def setUp(self):
        # config test_client
        app.config['TESTING'] = True
        self.app = app.test_client()

    def tearDown(self):
        # we have nothing to teardown
        pass

    def test_predict(self):
        post_data = json.dumps({
            "model_name": "dnn_model",
            "version": "001",
            "instances": [
                [8, 390.0, 190.0, 3850.0, 8.5, 70, 0, 0, 1]
            ]
        })
        rv = self.app.post('/predict', data=post_data, content_type='application/json')
        data = rv.get_json()
        self.assertEqual(rv.status_code, 200)
        self.assertIsInstance(data, dict)
        self.assertEqual(data["retcode"], 200)
        self.assertIn('Prediction', data['retmsg'])
        self.assertIsInstance(data['data'], dict)
        self.assertIn('predictions', data['data'])

    def test_predict_file(self):
        test_file_path = os.path.join(
            os.path.abspath(
                os.path.dirname(os.path.realpath(__file__))),
            os.pardir,
            'train',
            'datasets',
            'example_data.csv'
        )
        self.assertTrue(os.path.exists(test_file_path))
        post_data = {
            "model_name": "dnn_model",
            "version": "001",
            "file": (open(test_file_path, 'rb'), 'example_data.csv')
        }
        rv = self.app.post('/predict_file', data=post_data)
        data = rv.get_json()
        self.assertEqual(rv.status_code, 200)
        self.assertIsInstance(data, dict)
        self.assertEqual(data['retcode'], 200)
        self.assertIn('Prediction', data['retmsg'])
        self.assertIsInstance(data['data'], dict)
        self.assertIn('predictions', data['data'])
