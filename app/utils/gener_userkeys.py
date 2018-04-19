import rsa

def genrsa():
    pubkey,privkey = rsa.newkeys(2048)
    return {"pubKey":pubkey.save_pkcs1(),"priKey":privkey.save_pkcs1()}

