import datetime
import requests
from flask import current_app
def to_email(email,token):
    mail_dict={
                "title": "登录跳板机Token",
                "content":"您的Tokey：%s" % token ,
                "receivers":email
                }
    try:
        requests.post(url=current_app.config["MAIL_API"],data=json.dumps(mail_dict))
        return True
    except Exception as e:
        print(e)
        return False

def to_sms(phnum,token):
    sms_dict={
            "content":"您的Tokey：%s" % token ,
            "mobile":phnum
            }
    try:
        requests.post(url=current_app.config["SMS_API"],data=json.dumps(sms_dict)) 
        return True
    except Exception as e:
        return False

def to_weixin(openid,token):
    weixin_dict={
                "first":"跳板机token",
                "device":"跳板机",
                "time":datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "remark":"您的Tokey：%s" % token ,
                "openids":[openid]
                }
    try:
        requests.post(url=current_app.config["WEIXIN_API"],data=json.dumps(sms_dict))
        return True
    except Exception as e:
        return False

