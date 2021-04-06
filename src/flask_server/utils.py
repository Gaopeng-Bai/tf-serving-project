"""
coding: utf-8
python: 3.7.6
Date: 2021-04-04 00:26:34
@Software: VsCode
@Author: Gaopeng Bai
@Email: gaopengbai0121@gmail.com
@Description:
"""

from flask import jsonify


def get_json_result(retcode=0, retmsg='success', data=None):
    result_dict = {"retcode": retcode, "retmsg": retmsg, "data": data}
    response = {}
    for key, value in result_dict.items():
        if not value and key != "retcode":
            continue
        else:
            response[key] = value
    return jsonify(response), retcode
