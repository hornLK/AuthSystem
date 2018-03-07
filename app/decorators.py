from functools import wraps
from flask import abort,current_app,jsonify
import time,hashlib

def auth_api_valid(data):
    """
        用于验证APi的方法
    """
    try:
        encryption,time_span = data.split('|')
        time_span = float(time_span)
        if (time.time()-time_span) > current_app.config["AUTH_API_RANGE"]:
            return False
        hash_obj = hashlib.md5()
        hash_obj.update("%s|%f" % (current_app.config["SECRET_API_KEY"],time_span))
        if hash_obj.hexdigest() == encryption:
            return True
        else:
            return False
    except Exception as  e:
        pass
    return False

def api_auth(request):
    """
        用于验证api的装饰器
    """
    print("+++hehda")
    print(dir(request))
    def wrapper(func):
        def _wrapper():
            print(dir(request))
            security_key = request.headers.get("HTTP_SECRETKEY",None)
            if not security_key:
                return jsonify({'status':"Unauthorized"})
            if not auth_api_valid(security_key):
                return jsonify({"status":"Unauthorized"})
            return func()
        return _wrapper
    return wrapper
