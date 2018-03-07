from . import db
import hashlib,json
from datetime import datetime
from flask import current_app,request,jsonify
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


class UserToHosts(db.Model):
    __tablename__ = "usertohosts"
    user_id = db.Column(db.Integer,db.ForeignKey("users.id"),primary_key=True)
    host_id = db.Column(db.Integer,db.ForeignKey("hosts.id"),primary_key=True)
    role_id = db.Column(db.Integer,db.ForeignKey("roles.id"))

class User(UserMixin,db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    email = db.Column(db.String(64),unique=True,index=True)
    username = db.Column(db.String(64),unique=True,index=True)
    confirmed = db.Column(db.Boolean,default=True)
    create_at = db.Column(db.DateTime)
    last_seen = db.Column(db.DateTime,default=datetime.now)
    authlog = db.relationship("AuthLog",backref='user')
    userTohost = db.relationship("UserToHosts",
                                 foreign_keys=[UserToHosts.host_id],
                                 backref=db.backref('host',lazy='joined'),
                                 lazy='dynamic',
                                 cascade='all,delete-orphan')
    #返回静态数据方法
    def to_dic(self):
        dic = {
            id:self.id,
            email:self.email,
            username:self.username,
            confirmed:self.confirmed,
            create_at:self.create_at,
            last_seen:self.last_seen,
        }
        return dic
    def __repr__(self):
        return "<user:%s>" % self.email
    #generate_confi
    def generate_confirmation_token(self,expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'],expires_in = expiration)
        return s.dumps({'confirm_username':self.username}).decode('utf-8')
    @staticmethod
    def verify_auth_token(username,token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        if data.get("confirm_username")==username:
            return username
        else:return None
    #ban user login
    def confirm_login(self,action):
        if action:
            self.confirmed = True
        else:
            self.confirmed = False
            db.session.add(self)

class Hosts(db.Model):
    __tablename__ = "hosts"
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    hostName = db.Column(db.String(64),unique=True,index=True)
    hostIP = db.Column(db.String(64),index=True)
    hostPort = db.Column(db.Integer,default=22)
    hostGroup_id = db.Column(db.Integer,db.ForeignKey('hostgroup.id'))
    hostTouser = db.relationship("UserToHosts",
                                 foreign_keys=[UserToHosts.user_id],
                                 backref=db.backref('user',lazy='joined'),
                                 lazy='dynamic',
                                 cascade='all,delete-orphan')

    def __repr__(self):
        return "<name-ip:%s-%s>" % (self.hostName,self.hostIP)

class HostGroup(db.Model):
    __tablename__ = "hostgroup"
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    produceName = db.Column(db.String(64),unique=True)
    moMent = db.Column(db.String(128))
    hosts = db.relationship("HostGroup",backref="hostgroup")

    def updateName(self):
        pass
    def __repr__(self):
        return "produceName:%s" % ProduceName

class Role(db.Model):
    __tablename__ = "roles"
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    roleName = db.Column(db.String(64),unique=True,index=True)
    pubKey = db.Column(db.String(64))
    priKey = db.Column(db.String(64))
    moMent = db.Column(db.String(128))
    hostAndhost = db.relationship("UserToHosts",backref='role')

    def updatePubKey():
        pass
    def updatePriKey():
        pass


class AuthLog(db.Model):
    __tablename__ = "authlog"
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    user_id = db.Column(db.Integer,db.ForeignKey("users.id"))
    authTime = db.Column(db.DateTime)
    returnInfo = db.Column(db.String(32))
