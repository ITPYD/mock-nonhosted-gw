#from project.base_webservice import BaseWebService
import json
from project.BaseWebService import BaseWebService


class CZWebService(BaseWebService):
    """
    Example usage:

      from CZWebService import CZWebService


      ws = CZWebService(api_key_id='key_id', api_key_secret='key_secret')
      try:
        res = ws.login()
        print res
      except Exception as e:
        print e
    """
    mSecret = ""
    mMerchantInq = {}


    def merchant_update_url(self, mid, threed_url="", status_url=""):
        
        self.login()
        merchant_res = self.merchant_inq(mid)
        req = self.ReMap(merchant_res)

        # Clean up (Part I)
        del req["commonReqHeader"]["processingEnd"]
        del req["commonReqHeader"]["processingStart"]
        del req["commonReqHeader"]["respCode"]
        del req["commonReqHeader"]["respDetail"]
        del req["inputCommonServDtls"]["msgCode"]
        del req["inputCommonServDtls"]["msgDesc"]
        del req["inputCommonServDtls"]["inpArrDtls4"]
        del req["inputCommonServDtls"]["inpArrDtls3"]
        # Clean up (Part II)
        del req["inputCommonServDtls"]["inpF07"]
        del req["inputCommonServDtls"]["inpF08"]
        del req["inputCommonServDtls"]["inpF09"]
        del req["inputCommonServDtls"]["inpF10"]
        del req["inputCommonServDtls"]["inpF12"]
        del req["inputCommonServDtls"]["inpF14"]
        del req["inputCommonServDtls"]["inpF15"]
        del req["inputCommonServDtls"]["inpF17"]
        del req["inputCommonServDtls"]["inpF18"]
        del req["inputCommonServDtls"]["inpF19"]
        del req["inputCommonServDtls"]["inpF20"]
        del req["inputCommonServDtls"]["inpF24"]
        del req["inputCommonServDtls"]["inpF25"]

        # Common Header
        req["commonReqHeader"]["functionId"] = "UpdateMercInfo"
        req["commonReqHeader"]["tokenId"] = self.mSecret

        # inputCommonServDtls
        req["inputCommonServDtls"] = self.Replace(req["inputCommonServDtls"], "inpF05", "I")
        req["inputCommonServDtls"] = self.Replace(req["inputCommonServDtls"], "inpF27", "01")
        req["inputCommonServDtls"] = self.Replace(req["inputCommonServDtls"], "inpF28", "BRANCH PAYDE")  
        req["inputCommonServDtls"] = self.Replace(req["inputCommonServDtls"], "inpF29", "ecomref")
        req["inputCommonServDtls"] = self.Replace(req["inputCommonServDtls"], "inpF30", "commented out")

        # inpArrDtls
        for iter in req["inputCommonServDtls"]["inpArrDtls"]:
            iter = self.Replace(iter, "inpArrF01", "MAIN")
            iter = self.Replace(iter, "inpArrF02", "0001")
            iter = self.Replace(iter, "inpArrF03", "MR")
            iter = self.Replace(iter, "inpArrF14", "EN")
        # inpArrDtls3
        sub = {}
        sub["inpArrF01"] = "merfieldId"
        sub["inpArrF02"] = "E"
        req["inputCommonServDtls"]["inpArrDtls3"] = []
        req["inputCommonServDtls"]["inpArrDtls3"].append(sub)

        req["inputCommonServDtls"]["inpF33"] = threed_url
        req["inputCommonServDtls"]["inpF34"] = status_url

        #return req

        json_res = self.do('POST', '/ws/CommonService', req=req, auth=False)
        return json_res["outputCommonServDtls"]["msgCode"]
    
    """
    Merchant Inquiry
    """
    def merchant_inq(self, mid):
        req = {
                "commonReqHeader": {
                    "messageId": "ABC123",
                    "hostId": "JAMES",                                       
                    "functionId": "MercInquiry"                              
                },
                "inputCommonServDtls": {
                    "inpF01": mid                         
                }
            }

        json_res = self.do('POST', '/ws/CommonService', req=req, auth=False)
        print(json_res['outputCommonServDtls'])

        return json_res

    """
    Login
    """
    def login(self):
        
        req = {
            "commonReqHeader": {
                "messageId": "ABC123",
                "hostId": "JAMES",
                "functionId": "CallLogin"
                },
            "inputCommonServDtls": {
                "inpF01": "james",
                "inpF02": "c@rdz0n3"
                }
            }
        json_res = self.do('POST', '/ws/CommonService', req=req, auth=False)
        #print(json_res['outputCommonServDtls'])

        if "outputCommonServDtls" in json_res and "msgCode" in json_res['outputCommonServDtls']:
            msg_code = json_res['outputCommonServDtls']['msgCode']
            if msg_code == '00':
                self.mSecret = json_res['outputCommonServDtls']['outF02']

        return json_res

    '''
        Remap JSON output as input
    '''
    def ReMap(self, input):

        retype = type(input)
        if retype == type({}):
        
            output = {}

            for key in input:
                new_key = key.replace("output", "input")
                new_key = new_key.replace("out", "inp")
                new_key = new_key.replace("commonRespHeader", "commonReqHeader")
                
                map = self.ReMap(input[key])
                #print(f"{new_key} = {type(map)} = {len(map)} = [{map}]")
                if len(map) > 0:
                    output[new_key] = map

            return output

        elif retype == type([]):

            output = []

            for iter in input:
                output.append(self.ReMap(iter))

            return output
        else:
            return input

        return

    '''
        Replace 
    '''
    def Replace(self, input, key, val, force=False):

        old_val = ""
        if key in input:
            old_val = input[key]

        if force == True or len(old_val) == 0:
            input[key] = val

        return input

# vi: ft=python
