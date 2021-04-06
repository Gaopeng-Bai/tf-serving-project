#!/usr/bin/python3
# -*-coding:utf-8 -*-

# Reference:**********************************************
# @Time    : 4/6/2021 12:40 PM
# @Author  : Gaopeng.Bai
# @File    : test_with_requests.py
# @User    : gaope
# @Software: PyCharm
# @Description: 
# Reference:**********************************************

import requests
import json
import os

url = "http://127.0.0.1:32000/predict"
url_file = "http://127.0.0.1:32000/predict_file"


def test_predict():
    payload = json.dumps({
      "model_name": "export_model",
      "version": "2",
      "instances": [
        [10, 8, 2, 1, 23, 3, 1, 3, 1]
      ]
    })
    headers = {
      'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)


def test_predict_file():
    payload = {'model_name': 'dnn_model',
               'version': '001'}
    # file path
    path = '../src/train/datasets/example_data.csv'
    if os.path.isfile(path):
        files = [
            ('file', ('example_data.csv', open(path, 'rb'), 'text/csv'))
        ]
        headers = {}

        response = requests.request("POST", url_file, headers=headers, data=payload, files=files)

        print(response.text)


if __name__ == "__main__":
    test_predict_file()
