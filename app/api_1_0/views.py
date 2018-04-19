from flask_httpauth import HTTPBasicAuth
from flask import jsonify,request,current_app,url_for
from sqlalchemy import and_
from .. import db
from ..models import User,Hosts,Role,UserToHosts,UserKey
from . import api
from flask_restful import Resource,reqparse
from ..decorators import api_auth
from ..utils.send_token import to_email,to_sms,to_weixin
from ..utils.send_key import email_sendkey
import json
import datetime
from ..utils.gener_userkeys import genrsa

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
    else:
        return jsonify([])
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
            if data.get("weixinnumber"):
                user_obj.weixinnumber=int(data.get("weixinnumber"))
            user_obj.confirmed = data.get("confirmed")
            db.session.add(user_obj)
            try:
                db.session.commit()
                return jsonify({"status":True})
            except Exception as e:
                db.session.rollback()
                return jsonify({"status":False,"message":str(e)})
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

#获取用户公钥
@api.route('/auths/user/key/',methods=["GET"])
@api_auth(request)
def GetUserKey():
    if request.method == "GET":
        try:
            username = request.args.get("username").strip()
            user = User.query.filter_by(username=username).first()
            dir(user)
            pubkey = user.userkey.userPubkey
            prikey = user.userkey.userPrikey
            return jsonify({"status":True,"pubkey":pubkey,"prikey":prikey})
        except Exception as e:
            print(e)
            return jsonify({"status":False,"error":str(e)})
    return jsonify({"status":False,"error":"error request method"})

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

#去除用户主机权限
@api.route('/auths/user/delhost/',methods=['POST'])
@api_auth(request)
def Deluserhost():
    data = json.loads(request.data.decode("utf-8"))
    try:
        for host_id,user_id in data.items():
            uth = UserToHosts.query.filter(and_(UserToHosts.user_id==int(user_id),
                                    UserToHosts.host_id==int(host_id))).first()
            db.session.delete(uth)
        else:
            try:
                db.session.commit()
                return jsonify({"status":True})
            except:
                db.session.rollback()
    except Exception as e:
        return jsonify({"status":False})



#获取主机列表
@api.route('/auths/host/list/',methods=['GET'])
@api_auth(request)
def ShowAllHosts():
    hosts = Hosts.query.all()
    if hosts:
        result=[host.to_json() for host in hosts]
        return jsonify(result)
    else:
        return jsonify({"status":False})

#分页获取用户列表
@api.route('/auths/user/page/list/',methods=['GET'])
@api_auth(request)
def ShowPageUsers():
    try:
        page = request.args.get('page',1,type=int)
        pagination = User.query.paginate(
            page,per_page=current_app.config["AUTHSYSTEM_MESSAGE_PAGE"],
            #page,per_page=1,
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

#获取用户主机的角色
@api.route('/auths/user/host/list/',methods=['GET'])
@api_auth(request)
def UserHostRole():
    try:
        username = request.args.get("username",None)
        hostname = request.args.get("hostname",None)
        hostip = request.args.get("ip",None)
        if username is None:
            raise ValueError("User no login")
        user_id = User.query.filter_by(username=username).first().id
        if hostname is None and hostip is None:
            raise ValueError("Input hostname/ip")
        if  hostname:
            host_id = Hosts.query.filter_by(hostName=hostname).first().id
        else:
            host_id = Hosts.query.filter_by(hostIP=hostip).first().id
        uth = UserToHosts.query.filter(and_(UserToHosts.user_id==user_id,
                                        UserToHosts.host_id==host_id)).first()
        role = uth.role.roleName
        return jsonify({"status":True,"role":role})
    except Exception as e:
        print(e)
        return jsonify({"status":False,"error":str(e)})


#分页获取用户所有主机
@api.route('/auths/user/hosts/page/list/',methods=['GET'])
@api_auth(request)
def ShowPageUserHosts():
    try:
        user_id = request.args.get("user_id")
        page = request.args.get("page",1,type=int)
        pagination = UserToHosts.query.filter(UserToHosts.user_id==user_id).paginate(
            page,per_page=current_app.config["AUTHSYSTEM_MESSAGE_PAGE"],error_out=False
            #page,per_page=1,error_out=False
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
        pagination = Hosts.query.order_by(Hosts.id).filter(Hosts.id.notin_([host.hosts.id  for host in
                                                         User.query.get(int(user_id)).hosts])).paginate(
            page,per_page=current_app.config["AUTHSYSTEM_MESSAGE_PAGE"],error_out=False
            #page,per_page=3,error_out=False
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
@api.route('/auths/user/create/',methods=['POST'])
@api_auth(request)
def AddLoginUser():
    try:
        data = json.loads(request.data.decode("utf-8"))
        old_user = User.query.filter_by(email=data.get("email",None)).first()
        if old_user:
            raise ValueError("用户已存在")
        create_time=datetime.datetime.now()
        pk = genrsa()
        user = User(email=data.get("email"),
                   username=data.get("username"),
                   chinese=data.get("chinese"),
                   phonenumber=data.get("phonenumber"),
                   create_at=create_time)
        db.session.add(user)
        db.session.commit()
        user  = User.query.filter_by(email=data.get("email")).first()
        if not user:
            raise ValueError("添加失败")
        uk_dic = {"userPubkey":pk.get("pubKey").decode("utf-8"),
                "userPrikey":pk.get("priKey").decode("utf-8"),
                "keyUpdate":create_time,
                "user_id":user.id}
        uk = UserKey(**uk_dic)
        db.session.add(uk)
        db.session.commit()
        email_sendkey(user.email,user.userkey.userPubkey,user.userkey.userPrikey)
        return jsonify({"message":"用户创建成功","status":True})
    except Exception as e :
        print(e)
        db.session.rollback()
        return jsonify({"error":str(e),"status":False})

@api.route('/auths/login/apply/',methods=['POST'])
@api_auth(request)
def ApplyTokenHosts():
    try:
        data = json.loads(request.data.decode("utf-8"))
        username = data.get("username",None)
        channel = data.get("channel",0)
        user = User.query.filter_by(username=username).first()
        if user is None:
            raise ValueError("User not found")
        if not user.confirmed:
            raise ValueError("No login permissions")
        else:
            result = user.generate_confirmation_token()
            if int(channel) == 0:
                to_email(user.email,result[0])
            elif int(channel) == 1:
                if not user.phonenumber:
                    raise ValueError("telephone number is null")
                else:
                    to_sms(user.phonenumber,result[0])
            elif int(channel) == 2:
                if not user.weixinnumber:
                    raise ValueError("weixin number is null")
                else:
                    to_weixin(user.weixinnumber,result[0])
            return jsonify({"token":result[0],"hosts":result[1],"status":True}),200
    except Exception as e:
            print(e)
            return jsonify({"error":str(e),"status":False}),200

#测试api验证用例
@api.route('/auths/test/authapi/',methods=['GET'])
@api_auth(request)
def auth_api_test():
    return jsonify({"status":"ok"})
