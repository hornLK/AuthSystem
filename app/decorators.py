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
        secret_data = "%s|%f" % (current_app.config["SECRET_API_KEY"],time_span)
        hash_obj = hashlib.md5(secret_data.encode("utf-8"))
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
    def wrapper(func):
        @wraps(func)
        def _wrapper():
            security_key = request.headers.get("X-Http-Secretkey",None)
            if not security_key:
                return jsonify({'status':"Unauthorized"})
            if not auth_api_valid(security_key):
                return jsonify({"status":"Unauthorized"})
            return func()
        return _wrapper
    return wrapper
