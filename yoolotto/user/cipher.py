from Crypto.Cipher import AES
import base64
from django.http.response import HttpResponse


key = 'yoolotto@spa12345678901234567891'

#new_key = 'TSSSDAKJAA@SPA123LOTTO@CRACKED@@199'
new_key = 'TSSDAKJAA@SPA@LOTTO@KRLIYACRACKE'

def _unpad(s):
	return s[:-ord(s[len(s)-1:])]

def iOSdecryption(enc):
    print "enc",enc
    enc = base64.b64decode(enc)
    iv = 16 * '\x00'
    cipher = AES.new(key, AES.MODE_CBC, iv )
    decrypted_text = cipher.decrypt(enc)
    padded_decryption = _unpad(decrypted_text)
    return padded_decryption

def iOSdecryptionsecurity(enc):
    print "enc",enc
    enc = base64.b64decode(enc)
    iv = 16 * '\x00'
    cipher = AES.new(new_key, AES.MODE_CBC, iv )
    decrypted_text = cipher.decrypt(enc)
    padded_decryption = _unpad(decrypted_text)
    return padded_decryption

def androidDecryptionsecurity(enc):
    enc = base64.b64decode(enc)
    print enc
    cipher = AES.new(new_key, AES.MODE_ECB)
    aa = cipher.decrypt(enc)
    return _unpad(aa)

def androidDecryption(enc):
    enc = base64.b64decode(enc)
    print enc
    cipher = AES.new(key, AES.MODE_ECB)
    aa = cipher.decrypt(enc)
    return _unpad(aa)

