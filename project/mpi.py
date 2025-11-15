
import requests
import json
import base64
from project.key import Key
from flask import Response
from project import app
#from datetime import datetime

class MPI:
  
    mMpiPubKey = ""
    mTrxnId = ""
    mMerchantId = ""
    mUrl = ""
    pubkey = ""

    def __init__(self, mid, trxnId, url):
        self.mTrxnId = trxnId
        self.mMerchantId = mid
        self.mUrl = url

    #def InitGw(self, merchantId, trxId):
    def InitGw(self):

        headers = { 
            'Content-Type' : 'application/json'
        }

        k = Key()
        k.GenKeys()
        self.pubkey = k.GetPublicKey()
        body = {
            "merchantId" : self.mMerchantId,
            "pubKey" : self.pubkey,
            "purchaseId" : self.mTrxnId
        }

        try:
            url = self.mUrl + "/mkReq"
            print(f"URL: {url}")
            r = requests.post(url, headers = headers, data = json.dumps(body), verify=False)
            result=f"{r.status_code} {r.content}"    
            print(f">>> Status:{r.status_code} Content:{r.content}" )
            
            #r.content.decode("utf-8") # Convert the binary result to string
            j = json.loads(r.content.decode("utf-8"))

            if j['errorCode'] == '000':
                self.mMpiPubKey = j['pubKey']
                result = self.mTrxnId

        except Exception as e:
            error = str(e)
            result=error
        
        #return Response(result, status=200)
        print(result)
        return result

    def Sign(self, data):
        print("=====Sign=====")
        print(data)

        k = Key()
        k.pubkey = self.pubkey
        return k.Sign(data)

