from flask_httpauth import HTTPBasicAuth
from flask import jsonify,request
from ..models import User
from . import api
from flask_restful import Resource,reqparse
from ..decorators import api_auth

#获取用户列表
@api.route('/user/list/',methods=['GET'])
@api_auth(request)
def ShowAllUsers():
    users = User.query.all()
    if users:
        result=[user.to_dict() for user in users]
        return jsonify(result)

#用户登录申请token
'''
request:
    headers = {'content-type': 'application/json',"Http-Secretkey":xxx}
    #需要添加认证密钥
    data = {"username":"liukaiqiang"}
return:
    {
        "token":"xxx" ,
        "hosts":[
            {
                ...
            }
        ]
    }
'''
@api.route('/login/apply/',methods=['POST'])
@api_auth(request)
def ApplyTokenHosts():
    _,username=request.data.decode("utf-8").split("=")
    userObj = User.query.filter_by(username=username).first()
    result = userObj.generate_confirmation_token()
    return jsonify({"token":result[0],"hosts":result[1]}) ,200


#测试api验证用例
@api.route('/test/authapi/',methods=['GET'])
@api_auth(request)
def auth_api_test():
    return jsonify({"status":"ok"})
