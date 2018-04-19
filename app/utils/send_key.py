import datetime
import requests
from flask import current_app
def email_sendkey(email,pubkey,prikey):
    mail_dict={
                "title": "登录跳板机密钥",
                "receivers":email,
                "pubkey":pubkey,
                "prikey":prikey
                }
    try:
        requests.post(url=current_app.config["MAIL_API"],data=json.dumps(mail_dict))
        return True
    except Exception as e:
        print(e)
        return False

