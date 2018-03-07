from flask_httpauth import HTTPBasicAuth
from flask import jsonify,request
from ..models import User
from . import api
from flask_restful import Resource,reqparse
from ..decorators import api_auth

@api.route('/user/userlit/',methods=['GET'])
def get_users():
    users = User.query.all()
    result=[user.to_dic for user in users]
    return jsonify(result)


@api.route('/token/get_token/',methods=['POST'])
def get_token():
    pass

@api.route('/test/api_auth/',methods=['GET'])
@api_auth(request)
def auth_api_test():
    return jsonify({"status":"ok"})
