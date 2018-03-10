import requests,time,hashlib

def sent_test(url,api_key):
    SECRET_API_KEY = api_key
    time_span = time.time()
    secret_data = "%s|%f" % (SECRET_API_KEY,time_span)
    hash_obj = hashlib.md5(secret_data.encode("utf-8"))
    encryption = hash_obj.hexdigest()
    send_data = encryption+"|"+str(time_span)
    headers = {'content-type': 'application/json',"X-Http-Secretkey":send_data}
    res = requests.get(url,headers=headers)
    print(res.text)

if __name__ == "__main__":
    api_key = "0a37511d-be7d-4fdd-ab17-28b6c659d763"
    url = "http://192.168.220.3:8890/apiv1/auths/user/list/"
    sent_test(url,api_key)
