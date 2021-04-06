"""
coding: utf-8
python: 3.7.6
Date: 2021-04-02 11:48:44
@Software: VsCode
@Author: Gaopeng Bai
@Email: gaopengbai0121@gmail.com
@Description:
"""
from flask import Flask, request, current_app
from werkzeug.utils import secure_filename

import requests
import os
import json
import csv
from io import StringIO
import logging
import sys

from .utils import get_json_result


app = Flask(__name__)
app.logger.setLevel(logging.INFO)
# allow upload file with maximum 4Mb file size
app.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024
# allow upload file with specified extension
ALLOWED_EXTENSIONS = {'csv'}
# get tf_server from environment variables 'TF_SERVER', default 'http://localhost:8501'
TF_SERVER = os.getenv('TF_SERVER', 'http://localhost:8501')
# fixed tf_server version, concat this with TF_SERVER
TF_SERVER_VERSION = '/v1/models/'


# filter illegal filenames
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


# handle Internal server error
@app.errorhandler(500)
def internal_server_error(e):
    current_app.logger.error(str(e))
    return get_json_result(retcode=500, retmsg=str(e))


# handle Method not allowed
@app.errorhandler(405)
def method_not_allowed(e):
    current_app.logger.error(str(e))
    return get_json_result(retcode=405, retmsg=str(e))


# handle Bad Request
@app.errorhandler(400)
def bad_request_error(e):
    current_app.logger.error(str(e))
    return get_json_result(retcode=400, retmsg=str(e))


# handle Not found
@app.errorhandler(404)
def not_found_error(e):
    current_app.logger.error(str(e))
    return get_json_result(retcode=404, retmsg=str(e))


# handle Request Entity Too Large
@app.errorhandler(413)
def request_entity_too_large_error(e):
    current_app.logger.error(str(e))
    return get_json_result(retcode=404, retmsg=str(e))


# hello world GET request
@app.route('/', methods=['GET'])
def hello_world():
    return get_json_result(retcode=200, retmsg='Hello World!')


# check health GET request
@app.route("/health", methods=['GET'])
def check_health():
    return get_json_result(retcode=200, retmsg='Healthy!')


# predict single/batch data POST request
@app.route('/predict', methods=['POST'])
def predict():
    # check if request`s content_type is 'application/json'
    if request.content_type != 'application/json':
        errmsg = "400 Bad Request. Please send request with 'application/json'."
        current_app.logger.error(errmsg)
        return get_json_result(retcode=400, retmsg=errmsg)
    # get json data from request
    json_params = request.get_json()
    # get model_name
    model_name = json_params.get("model_name")
    # check model_name existence which is a must
    if model_name is None:
        errmsg = "400 Bad Request. Please provide model_name in 'model_name' section."
        current_app.logger.error(errmsg)
        return get_json_result(retcode=400, retmsg=errmsg)
    # check version existence
    version = json_params.get('version')
    # check label existence
    label = json_params.get('label')
    # form model full name
    model_to_use = form_model_to_use(model_name, version, label)
    # check instances existence which is a must
    if "instances" not in json_params:
        errmsg = "400 Bad Request. Please provide data in 'instances' section."
        current_app.logger.error(errmsg)
        return get_json_result(retcode=400, retmsg=errmsg)
    # form request url
    request_url = TF_SERVER + TF_SERVER_VERSION + model_to_use + ':predict'
    # make POST request to TF-serving
    r = requests.post(request_url, json={'instances': json_params.get('instances')})
    # load response data from TF-serving, then load to json
    response_data = json.loads(r.content.decode('utf-8'))
    # check whether TF-serving response is succeeded
    if r.status_code != 200:
        return get_json_result(retcode=r.status_code, retmsg="Prediction encountered error", data=response_data)
    # when everything is fine, return prediction
    return get_json_result(retcode=200, retmsg="Prediction succeeded!", data=response_data)


# predict csv file POST request
@app.route('/predict_file', methods=['POST'])
def predict_file():
    # get file from request
    upload_file = request.files['file']
    # check whether uploaded file is legal
    if not upload_file or not allowed_file(secure_filename(upload_file.filename)):
        errmsg = "400 Bad Request. Invalid csv file."
        current_app.logger.error(errmsg)
        return get_json_result(retcode=400, retmsg=errmsg)
    # get form data from request
    form_data = request.form
    # get model_name
    model_name = form_data.get('model_name')
    # check model_name existence which is a must
    if model_name is None:
        errmsg = "400 Bad Request. Please provide model_name in 'model_name' section."
        current_app.logger.error(errmsg)
        return get_json_result(retcode=400, retmsg=errmsg)
    # check version existence
    version = form_data.get('version')
    # check label existence
    label = form_data.get('label')
    # csv reader from upload_file.stream
    reader = csv.reader(StringIO(upload_file.stream.read().decode('utf-8')))
    # skip header
    next(reader, None)
    data_list = []
    for row in reader:
        # skip index
        data_list.append([float(feature) for feature in row[1:]])
    # check instances existence which is a must
    model_to_use = form_model_to_use(model_name, version, label)
    # form request url
    request_url = TF_SERVER + TF_SERVER_VERSION + model_to_use + ':predict'
    request_data = {'instances': data_list}
    # make POST request to TF-serving
    current_app.logger.info(f'Predicting model {model_name} with version {version} and/or label {label}')
    # load response data from TF-serving, then load to json
    r = requests.post(request_url, json=request_data)
    # load response data from TF-serving, then load to json
    response_data = json.loads(r.content.decode('utf-8'))
    # check whether TF-serving response is succeeded
    if r.status_code != 200:
        return get_json_result(retcode=r.status_code, retmsg="Prediction encountered error", data=response_data)
    # when everything is fine, return prediction
    return get_json_result(retcode=200, retmsg="Prediction succeeded!", data=response_data)


def form_model_to_use(model_name, version, label):
    # http: // host: port / v1 / models /${MODEL_NAME}[ / versions /${VERSION} | / labels /${LABEL}]:predict
    model_to_use = model_name
    if version is not None:
        model_to_use += '/versions/' + version
    if label is not None:
        model_to_use += '/labels/' + label
    return model_to_use


if __name__ == '__main__':
    app.run(ip="0.0.0.0", port="5000")
