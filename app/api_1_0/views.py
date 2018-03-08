from flask_httpauth import HTTPBasicAuth
from flask import jsonify,request
from ..models import User
from . import api
from flask_restful import Resource,reqparse
from ..decorators import api_auth

@api.route('/user/userlit/',methods=['GET'])
@api_auth(request)
def get_users():
    users = User.query.all()
    result=[user.to_dic for user in users]
    return jsonify(result)


@api.route('/token/achieve_token/',methods=['POST'])
@api_auth(request)
def achieve_token():
    _,username=request.data.decode("utf-8").split("=")
    print(username)
    userObj = User.query.filter_by(username=username).first()
    re_token = userObj.generate_confirmation_token(20)
    return jsonify({"token":re_token}) ,200

@api.route('/test/api_auth/',methods=['GET'])
@api_auth(request)
def auth_api_test():
    return jsonify({"status":"ok"})
