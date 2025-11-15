#!/usr/bin/python3

# Resources:
# https://github.com/UglyBaliCode/RSA-Encryption-with-Python/tree/master/sign%20and%20verify
# https://www.youtube.com/watch?v=LCZ7PcYGxew

from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
import json
import base64
from project import app, db

class Key:
    public_key_path = app.config['KEY_PATH'] + "/public.key"
    private_key_path = app.config['KEY_PATH'] + "/private.key"
    
    # Debug purpose
    pubkey = ""
    # Debug purpose

    def GenKeys(self):

        key = RSA.generate(2048)
        private_key = key.export_key()
        file_out = open(self.private_key_path, "wb")
        file_out.write(private_key)
        file_out.close()

        public_key = key.publickey().export_key()
        file_out = open(self.public_key_path, "wb")
        file_out.write(public_key)
        file_out.close()

    def GetPublicKey(self):
        print('==GetPublicKey==')
        pubkey = open(self.public_key_path).read()
        pubkey = pubkey.replace('-----BEGIN PUBLIC KEY-----','').replace('-----END PUBLIC KEY-----','')
        pubkey = pubkey.replace('+','-').replace('/','_').replace("\n", '').strip()
        print(pubkey)
        print("----------")
        return pubkey

    def Sign(self, data):
        print("===Sign[" + data + "]====")

        key = RSA.import_key(open(self.private_key_path).read())
        h = SHA256.new(data.encode()) # Need to convert to byte

        '''
        once hashing is done, we need to create a sign object through 
        which we can sign a message
        '''

        signer=pkcs1_15.new(key)
        signature=signer.sign(h)

        
        #### Explanation
        #print(signature.hex()) # Print out signature in hex
        #
        # Usually, signature is printed to file as it is.
        #file_out = open("xsignature.pem", "wb")
        #file_out.write(signature)
        #file_out.close()
        #
        # If the file is open and printed
        # E.g.
        #
        # sig=open("xsignature.pem", "rb").read()
        # print(sig)
        #
        # The output: 
        # b'\x04z\xe6\x19A\x03\x8d\xf1\xab\xce\x99f\xc9\xd8K\xe0\xefP_\x95\xc6\x93\xbc\x02\xa4dU\xe6\x05\xad\x07y\x88\x9fb\x9a=\xe6\xd0s\x89\xc8\xceH\x89?\x12\xe4\x8dB\xed`"7xd\x80C*B\xaf\x00\xfd\xfb\x1c\x82%T&3\xa9\xd9nc\x97\xa4\xf2\x95\n\x18\xe0\x89\x97/\xa8\xa6$W\x02#u\x94q\xf2\x99|<H~z\xa8\xbe\xf5\xf8B2<\xdcf\xc7\x08^\x91\x02\xee\xe1\xcab\xdd\xd4M\x04e\xdc \xee\xa7\x18q\xc5\x11\xa1\x84\xf3\x04b\xeb_\xd0\x81\xb48\x91.\xc7&\x8a\x83o$\xbe\xe6:\xfb@\xcf\x96Fw\xfc\xba\xc4r,\x860X\xea\x16\xa9\x1bl\x0b\x99\xbd\'n\xae\xb9b\x12\xf0\xc1/Q\x94-\xabeQ\xb0\xa8T(v_\x9c2\x9c\r\xe6\xba\x94C#\x0bD\xffe7\xdd\xb2\xc1l\xbbS\x82\x0b\xbd\xdeDW\xb4\x9d\xf0M\xca\x1bP{\x1f7
        #\xcd2(g\xd6\x08\x0c\xbf\xe0\x05\xf5\x81\xe6\xb3\x19\xac-\xdc\xb9W\x14=K\x87'
        #
        # Another way to base64 encode is to read from file.
        # E.g.
        #urlSafeEncodedBytes = base64.urlsafe_b64encode(open("xsignature.pem", "rb").read())
        #urlSafeEncodedStr = str(urlSafeEncodedBytes, "utf-8").replace('=','')
        #print(urlSafeEncodedStr)

        urlSafeEncodedBytes = base64.urlsafe_b64encode(signature)
        urlSafeEncodedStr = str(urlSafeEncodedBytes, "utf-8").replace('=','')
        
        print(urlSafeEncodedStr)
        print("-----------")
        #self.IsValidSign(self.pubkey, data, urlSafeEncodedStr)
        
        return urlSafeEncodedStr

    def IsValidSign(self, pubkey, data, signature):
        print("===IsValidSign====")

        result=False

        # Restore the signature
        signature = signature + "=="
        decoded_signature = base64.urlsafe_b64decode(signature) # This is the original signature (post base64 -d)

        # Restore pubkey 
        pubkey = pubkey.replace('-','+').replace('_','/')
        decoded_pubkey = "-----BEGIN PUBLIC KEY-----\n" + pubkey + "\n-----END PUBLIC KEY-----"

        # SHA first
        # message = b'SALES1234567890123455100000000000100TestUser25081232520210224112943458100N'
        #h = SHA256.new(message)
        h = SHA256.new(data.encode())
        
        #key = RSA.import_key(open('public.key').read())
        #key = RSA.import_key(open(self.public_key_path).read())
        key = RSA.import_key(decoded_pubkey)
        try:
            pkcs1_15.new(key).verify(h, decoded_signature)
            print ("The signature is valid.")
            return True
        except (ValueError, TypeError):
            print ("The signature is not valid.")

        return result


