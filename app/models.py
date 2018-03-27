from . import db
import hashlib,json
import datetime,time
from flask import current_app,request,jsonify
from flask_login import UserMixin
#from .email import send_email
from .utils import hashlib_token_serializer as Serializer

class UserToHosts(db.Model):
    '''
        用户与主机权限关系表
    '''
    __tablename__ = "usertohosts"
    user_id = db.Column(db.Integer,db.ForeignKey("users.id"),primary_key=True)
    host_id = db.Column(db.Integer,db.ForeignKey("hosts.id"),primary_key=True)
    role_id = db.Column(db.Integer,db.ForeignKey("roles.id"))
    hosts = db.relationship("Hosts",back_populates="users")
    users = db.relationship("User",back_populates="hosts")

class UserKey(db.Model):
    #用户跳板机上的key
    __tablename__ = "userkeys"
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    #公钥
    userPubkey = db.Column(db.String(256))
    #私钥
    userPrikey = db.Column(db.String(256))
    #密钥更新时间
    keyUpdate = db.Column(db.DateTime)
    user_id = db.Column(db.Integer,db.ForeignKey("users.id"))
    user = db.relationship("User",back_populates="userkey")

    def updateKey(self):
        pass

class User(UserMixin,db.Model):
    '''
    用户表
    方法:
        to_dic:
            return :{
                "id":id,
                "email":email,
                "username":username,
                "confirmed":confirmed,
                "create_at":create_at
            }   #返回用户对象数据的字典

        generate_confirmed_token:
            return:[
                "token":token,
                "hosts":[...]
                ]#返回用户的token和可登录机器的列表
        confirmed:
            #禁止用户登录方法

    '''

    __tablename__ = "users"
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    #邮箱
    email = db.Column(db.String(64),unique=True,index=True,nullable=False)
    #用户名
    username = db.Column(db.String(64),unique=True,index=True,nullable=False)
    #电话号码
    phonenumber = db.Column(db.Integer)
    #微信号
    weixinnumber = db.Column(db.String(32))
    #是否可以登录跳板机，默认为True
    confirmed = db.Column(db.Boolean,default=True)
    #用户key
    userkey = db.relationship("UserKey",back_populates="user")
    #用户创建时间
    create_at = db.Column(db.DateTime)
    #外键关联log表记录用户认证日志
    authlog = db.relationship("AuthLog",backref='user')
    #制定关联表关系
    hosts = db.relationship("UserToHosts",back_populates="users")
    #返回静态数据方法
    def to_json(self):
        to_json = {
            "id":self.id,
            "email":self.email,
            "username":self.username,
            "phonenumber":self.phonenumber,
            "weixinnumber":self.weixinnumber,
            "confirmed":self.confirmed,
            "create_at":self.create_at,
            "hostcount":self.hosts.__len__()
        }
        return to_json
    def __repr__(self):
        return "<user:%s>" % self.email

    #生成返回token以及服务器列表信息
    def generate_confirmation_token(self):

        time_stamp = time.time()
        return_token = Serializer.hashlib_generate_token(
            current_app.config['SECRET_KEY'],
            time_stamp,
            self.username
        )
        #发送日志方法
        #send_email(self.email,
        #           '跳板机登录验证token',
        #           'auth/email/user_token',
        #           user=self.username,token=return_token)

        #生成主机列表
        hosts = [{"hostInfo":host.hosts.to_json(),"role":host.role.roleName,"username":self.username} for host in self.hosts if self.hosts ]
       #定义用户日志信息 
        write_log = {"user_id":self.id,
                     "authTime":datetime.datetime.now(),
                     "returnToken":return_token
                    }
        #log
        authlog =  AuthLog(**write_log)
        print(authlog)
        db.session.add(authlog)
        db.session.commit()
        return [return_token,hosts]

    #远程认证用户方法
    @staticmethod
    def verify_auth_token(username,token,time_stamp):
        s = Serializer.hashlib_check_token(
            token,
            current_app.config['SECRET_KEY'],
            time_stamp,
            username
        )
        if s:
            return True
        else:False
    #禁止用户登录操作
    def confirm_login(self,action):
        if action:
            self.confirmed = True
        else:
            self.confirmed = False
            db.session.add(self)

class Hosts(db.Model):
    #主机表
    '''
    方法：
        to_json:
            return:{
                "id":1,
                "hostName":"host1",
                "hostIP":"192.168.1.1",
                "hostPort":22,
                "hostGroup":"测试平台"
            }
    '''
    __tablename__ = "hosts"
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    #主机名
    hostName = db.Column(db.String(64),unique=True,index=True)
    #主机ip
    hostIP = db.Column(db.String(64),index=True)
    #ssh连接port
    hostPort = db.Column(db.Integer,default=22)
    #关联到主机组
    hostGroup_id = db.Column(db.Integer,db.ForeignKey('hostgroup.id'))
    users = db.relationship("UserToHosts",back_populates="hosts")
    #主机信息
    def to_json(self):
        to_json={
            "id":self.id,
            "hostName":self.hostName,
            "hostIP":self.hostIP,
            "hostPort":self.hostPort,
            "hostGroup":self.hostgroup.produceName
        }
        return to_json

    def __repr__(self):
        return "<name-ip:%s-%s>" % (self.hostName,self.hostIP)

RoomHostGroup = db.Table('roomhostgroup',
                        db.Column('root_id',db.Integer,db.ForeignKey('rooms.id')),
                        db.Column('hostgroup_id',db.Integer,db.ForeignKey('hostgroup.id'))
                        )
class Room(db.Model):
    #机房表
    __tablename__ = "rooms"
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    roomName = db.Column(db.String(64),unique=True)
    moMent = db.Column(db.String(256))
    hostgroups = db.relationship("HostGroup",
                                secondary=RoomHostGroup,
                                 backref=db.backref('room',lazy='dynamic'),
                                 lazy='dynamic'
                                )

class HostGroup(db.Model):
    #主机组表
    '''
    方法：
        updateName:
            return:
                #完成主机组名更新操作
    '''
    __tablename__ = "hostgroup"
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    #业务线名
    produceName = db.Column(db.String(64),unique=True)
    #业务线描述
    moMent = db.Column(db.String(128))
    hosts = db.relationship("Hosts",backref="hostgroup")

    def updateName(self):
        pass
    def __repr__(self):
        return "produceName:%s" % self.produceName

class Role(db.Model):
    #角色表，也就是业务机登录用户名
    '''
    方法：
        updatePubKey:
            return:
                #更新公钥并通过ansible进行业务主机上公钥的更新
        updatePriKey:
            return:
                #更新私钥通过ansible进行跳板机上私钥的更新
    '''
    __tablename__ = "roles"
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    #角色名
    roleName = db.Column(db.String(64),unique=True,index=True)
    #存储公钥
    pubKey = db.Column(db.String(256))
    #存储私钥
    priKey = db.Column(db.String(256))
    #角色描述
    moMent = db.Column(db.String(128))
    userTohost = db.relationship("UserToHosts",backref='role')

    def updatePubKey():
        pass
    def updatePriKey():
        pass
    def to_json(self):
        to_json={
            "role_id":self.id,
            "role_name":self.roleName
        }
        return to_json

    def __repr__(self):
        return "roleName:%s" % self.roleName


class AuthLog(db.Model):
    #认证日志表
    __tablename__ = "authlog"
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    user_id = db.Column(db.Integer,db.ForeignKey("users.id"))
    authTime = db.Column(db.DateTime)
    returnToken = db.Column(db.String(128))
