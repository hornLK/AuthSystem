import hashlib,time

def hashlib_generate_token(secretkey,time_stamp,username):
    secretkey_data = "%s|%f|%s" % (secretkey,time_stamp,username)
    hash_obj = hashlib.md5(secretkey_data.encode("utf-8"))
    encryption = hash_obj.hexdigest()[4:12]
    return encryption

def hashlib_check_token(encryption,secretkey,time_stamp,username,expiration=20):
    try:
        time_stamp = float(time_stamp)
        if time.time() - time_stamp > expiration:
            return False
        secretkey_data = "%s|%f|%s" % (secretkey,time_stamp,username)
        if encryption == hashlib.md5(secretkey_data.encode("utf-8")).hexdigest()[4:12]:
            return True
    except Exception as e:
        return False

if __name__ == "__main__":
    secretkey="123123"
    time_stamp = time.time()
    username = "liukaiqiang"

    encryption = hashlib_generate_token(secretkey,time_stamp,username)
    print (encryption)

    result = hashlib_check_token(encryption,secretkey,time_stamp,username)
    print(result)
