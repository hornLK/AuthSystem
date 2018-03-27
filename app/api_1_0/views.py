from flask_httpauth import HTTPBasicAuth
from flask import jsonify,request,current_app,url_for
from sqlalchemy import and_
from .. import db
from ..models import User,Hosts,Role,UserToHosts
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
        result=[user.to_json() for user in users]
        return jsonify(result)
#获取角色列表
@api.route('/auths/role/list/',methods=['GET'])
@api_auth(request)
def ShowAllRoles():
    roles = Role.query.all()
    if roles:
        result = [role.to_json() for role in roles ]
        return jsonify(result)
#编辑用户信息
@api.route('/auths/user/edit/',methods=['POST'])
@api_auth(request)
def EditUsers():
    if request.method == "POST":
        try:
            data = json.loads(request.data.decode("utf-8"))
            data["user_id"]=int(data.get("user_id"))
            data["confirmed"] = True if data["confirmed"] == "True" else False
            user_obj = User.query.get_or_404(data.get("user_id"))
            user_obj.weixinnumber=int(data.get("weixinnumber"))
            user_obj.confirmed = data.get("confirmed")
            db.session.add(user_obj)
            try:
                db.session.commit()
            except:
                db.session.rollback()
            return jsonify({"status":True})
        except Exception as e:
            print(e)
            return jsonify({"status":False,"message":str(e)})

#编辑用户角色
@api.route('/auths/userrole/edit/',methods=["POST"])
@api_auth(request)
def EditUserRole():
    try:
        data = json.loads(request.data.decode("utf-8"))
        userrole_obj =UserToHosts.query.filter(and_(UserToHosts.user_id==int(data.get("user_id")),
                                                UserToHosts.host_id==int(data.get("host_id")))).first()
        userrole_obj.role_id = int(data.get("role_id"))
        db.session.add(userrole_obj)
        try:
            db.session.commit()
        except:
            db.session.rollback()
        return jsonify({"status":True})
    except Exception as e:
        print(e)
        return jsonify({"status":False})



#获取用户信息
@api.route('/auths/user/info/',methods=['GET'])
@api_auth(request)
def GetUserInfo():
    if request.method == "GET":
        try:
            user_id=int(request.args.get("user_id"))
            user_obj = User.query.get_or_404(user_id)
            user_info = user_obj.to_json()
            return jsonify({"user_info":user_info}),200
        except Exception as e:
            print(e)
            return jsonify({"message":str(e)}),404

#获取主机列表
@api.route('/auths/host/list/',methods=['GET'])
@api_auth(request)
def ShowAllHosts():
    hosts = Hosts.query.all()
    if hosts:
        result=[host.to_json() for host in hosts]
        return jsonify(result)

#分页获取用户列表
@api.route('/auths/user/page/list/',methods=['GET'])
@api_auth(request)
def ShowPageUsers():
    try:
        page = request.args.get('page',1,type=int)
        pagination = User.query.paginate(
            #page,per_page=current_app.config["AUTHSYSTEM_MESSAGE_PAGE"],
            page,per_page=1,
            error_out=False
        )
        users = pagination.items
        prev_page = None
        if pagination.has_prev:
            prev_page = int(page)-1
        next_page = None
        if pagination.has_next:
            next_page = int(page)+1
        return jsonify({
            "users":[user.to_json() for user in users ],
            "prev":prev_page,
            "next":next_page,
            "current":page,
            "total":pagination.total,
            "page_iter":[page_num for page_num in range(1,pagination.pages+1)]
        })
    except Exception as e:
        print(e)
        return jsonify({"status":False})
#分页获取主机列表
@api.route('/auths/host/page/list/',methods=['GET'])
@api_auth(request)
def ShowPageHosts():
    try:
        page = request.args.get('page',1,type=int)
        pagination = Hosts.query.paginate(
            page,per_page=current_app.config["AUTHSYSTEM_MESSAGE_PAGE"],
            error_out=False
        )
        hosts = pagination.items
        prev_page = None
        if pagination.has_prev:
            prev_page = url_for('api.ShowPageHosts',page=page-1,_external=True)
        next_page = None
        if pagination.has_next:
            next_page = url_for('api.ShowPageHosts',page=page+1,_external=True)
        return jsonify({
                "hosts":[host.to_json() for host in hosts],
                "prev":prev_page,
                "next":next_page,
                'count':pagination.total,
                'per_page':current_app.config["AUTHSYSTEM_MESSAGE_PAGE"]
            })
    except Exception as e:
        print(e)
        return jsonify({"status":False})
#分页获取用户所有主机
@api.route('/auths/user/hosts/page/list/')
@api_auth(request)
def ShowPageUserHosts():
    try:
        user_id = request.args.get("user_id")
        page = request.args.get("page",1,type=int)
        pagination = UserToHosts.query.filter(UserToHosts.user_id==user_id).paginate(
            #page,per_page=current_app.config["AUTHSYSTEM_MESSAGE_PAGE"],error_out=False
            page,per_page=1,error_out=False
        )
        user_hosts = pagination.items
        prev_page = None
        if pagination.has_prev:
            prev_page = int(page)-1
        next_page = None
        if pagination.has_next:
            next_page = int(page)+1
        return jsonify({
            "hosts":[{"host":host.hosts.to_json(),"role":host.role.to_json()} for host in user_hosts],
            "prev":prev_page,
            "next":next_page,
            "current":page,
            "page_iter":[page_num for page_num in range(1,pagination.pages+1)],
            "per_page":current_app.config["AUTHSYSTEM_MESSAGE_PAGE"]
        })

    except Exception as e:
        print(e)
        return jsonify({"status":False})

#获取不属于该用户的机器
@api.route('/auths/user/hosts/page/out-list/')
@api_auth(request)
def ShowPageUserOutHosts():
    try:
        user_id = request.args.get("user_id")
        page = request.args.get("page",1,type=int)
        print(user_id)
        pagination = Hosts.query.filter(Hosts.id.notin_([host.hosts.id  for host in
                                                         User.query.get(int(user_id)).hosts])).paginate(
            #page,per_page=current_app.config["AUTHSYSTEM_MESSAGE_PAGE"],error_out=False
            page,per_page=3,error_out=False
        )
        out_hosts = pagination.items
        prev_page = None
        if pagination.has_prev:
            prev_page = int(page)-1
        next_page = None
        if pagination.has_next:
            next_page = int(page)+1
        return jsonify({
            "hosts":[host.to_json() for host in out_hosts],
            "prev":prev_page,
            "next":next_page,
            "current":page,
            "page_iter":[page_num for page_num in range(1,pagination.pages+1)],
            "per_page":current_app.config["AUTHSYSTEM_MESSAGE_PAGE"]
        })

    except Exception as e:
        print(e)
        return jsonify({"status":False})

@api.route('/auths/user/authshosts/',methods=['POST'])
@api_auth(request)
def AuthHosts():
    try:
        data=json.loads(request.data.decode("utf-8"))
        user_id=int(data.get("user_id"))
        for k,v in data.get("host_role").items():
            role_id = Role.query.filter_by(roleName=v).first().id
            tmp_uth = UserToHosts(user_id=user_id,role_id=role_id,host_id=int(k))
            db.session.add(tmp_uth)
        else:
            try:
                db.session.commit()
            except:
                db.session.rollback()
        return jsonify({"status":True})
    except Exception as e:
        return jsonify({"status":False,"message":str(e)})

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
