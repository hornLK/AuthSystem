from flask_httpauth import HTTPBasicAuth
from flask import jsonify,request
from .. import db
from ..models import User,Hosts
from . import api
from flask_restful import Resource,reqparse
from ..decorators import api_auth
import json

#获取用户列表
@api.route('/auths/user/list/',methods=['GET'])
@api_auth(request)
def ShowAllUsers():
    users = User.query.all()
    if users:
        result=[user.to_dict() for user in users]
        return jsonify(result)

#编辑用户信息
@api.route('/auths/user/edit/',methods=['POST'])
def EditUsers():
    if request.method == "POST":
        try:
            data = json.loads(request.form.get("data"))
            data["user_id"]=int(data.get("user_id"))
            data["confirmed"] = True if data["confirmed"] == "True" else False
            user_obj = User.query.get_or_404(data.get("user_id"))
            user_obj.phonenumber=int(data.get("phonenumber"))
            user_obj.weixinnumber=int(data.get("weixinnumber"))
            db.session.add(user_obj)
            db.session.commit()
            return jsonify({"status":True})
        except Exception as e:
            return jsonify({"status":False,"message":str(e)})

#获取用户信息
@api.route('/auths/user/authuserinfo/',methods=['GET'])
@api_auth(request)
def GetUserInfo():
    if request.method == "GET":
        try:
            user_id=int(request.args.get("user_id"))
            user_obj = User.query.get_or_404(user_id)
            user_info = user_obj.to_dict()
            user_hosts = [{"host":host.hosts.to_dict(),"role":host.role.to_dict()} for host in user_obj.hosts]
            return jsonify({"hosts":user_hosts,"user_info":user_info}),200
        except Exception as e:
            print(e)
            return jsonify({"message":str(e)}),404
#获取主机列表
@api.route('/auths/host/list/',methods=['GET'])
@api_auth(request)
def ShowAllHosts():
    hosts = Hosts.query.all()
    if hosts:
        result=[host.to_dict() for host in hosts]
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
@api.route('/auths/login/apply/',methods=['POST'])
@api_auth(request)
def ApplyTokenHosts():
    _,username=request.data.decode("utf-8").split("=")
    userObj = User.query.filter_by(username=username).first()
    result = userObj.generate_confirmation_token()
    return jsonify({"token":result[0],"hosts":result[1]}) ,200


#测试api验证用例
@api.route('/auths/test/authapi/',methods=['GET'])
@api_auth(request)
def auth_api_test():
    return jsonify({"status":"ok"})
