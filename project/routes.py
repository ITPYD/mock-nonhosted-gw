import requests, os, random
from project import app, mail
from datetime import date, time, datetime, timedelta
from flask import current_app, render_template, redirect, url_for, flash, request, send_file, send_from_directory,  abort, Response, session
from flask_mail import Message
from project.forms import MpiForm
from project.mpi import MPI
from project.key import Key





# ---------------------
# MPI Function
# ---------------------    

# Not inused
@app.route('/checkout_iframe', methods=['GET','POST'])
def checkout_iframe():

    form = MpiForm()
    filename = request.args.get('filename')
    now = datetime.now().strftime("%Y%m%d%H%M%S")

    if filename == "None" or filename == None:
        print(f"the filename is None")
        # Load default value
        form.MPI_TRANS_TYPE.data 	= "SALES"
        form.MPI_MERC_ID.data       = app.config["MERCHANT_ID"]
        form.MPI_PAN.data           = "5100000000000107"
        form.MPI_CARD_HOLDER_NAME.data = "Test Card"
        form.MPI_PAN_EXP.data       = "2508"
        form.MPI_CVV2.data          = "123"
        form.MPI_TRXN_ID.data       = 'txid' + now
        form.MPI_PURCH_DATE.data 	= now
        form.MPI_PURCH_CURR.data 	= "458"
        form.MPI_PURCH_AMT.data 	= "100"
        form.MPI_ADDR_MATCH.data 	= "N"
    else:
        print(f"filename {{filename}} ")
        form.Load(filename)
        form.MPI_PURCH_DATE.data 	= now

    return render_template('MpiIframe.html', form=form, user=get_username(), is_admin=is_admin())

@app.route("/hosted", methods=['GET','POST'])
def hosted_iframe():
    now = datetime.now().strftime("%Y%m%d%H%M%S")

    # Load default value
    form = MpiForm()
    form.MPI_TRXN_ID.data       = 'tx' + now
    form.MPI_PURCH_DATE.data 	= now
    form.MPI_MERC_ID.data       = app.config['MERCHANT_ID'] 
    form.MPI_TRANS_TYPE.data    = "SALES"
    form.MPI_PURCH_CURR.data    = 458
    form.MPI_PURCH_AMT.data     = 1000

    return render_template('ihosted.html', form=form, user=get_username(), is_admin=is_admin())

@app.route("/nonhosted", methods=['GET','POST'])
def nonhosted_iframe():
    now = datetime.now().strftime("%Y%m%d%H%M%S")

    # Load default value
    form = MpiForm()
    form.MPI_TRXN_ID.data       = 'dev' + now
    form.MPI_PURCH_DATE.data 	= now
    return render_template('inonhosted.html', form=form, user=get_username(), is_admin=is_admin())    

@app.route('/sign_data_nonhosted', methods=['GET','POST'])
def sign_data_hosted():

    #print("---header---")
    #print(request.headers)
    
    print("------[sign_data]------")
    print(request.form)

    trans_type = "SALES"
    #trans_type = "INITRECURR"
    merc_id = app.config["MERCHANT_ID"]
    pan = request.form.get('MPI_PAN',"")
    cardholder_name = request.form.get('MPI_CARD_HOLDER_NAME',"")
    pan_exp = request.form.get('MPI_PAN_EXP',"")
    cvv2 = request.form.get('MPI_CVV2',"")
    trxn_id = request.form.get('MPI_TRXN_ID',"")
    puch_date = request.form.get('MPI_PURCH_DATE',"")
    purch_curr = "458"
    purch_amt = "10000"
    #purch_amt = request.form.get('MPI_PURCH_AMT',"")

    data = trans_type+merc_id+pan+cardholder_name+pan_exp+cvv2+trxn_id+puch_date+purch_curr+purch_amt
    print(data)
 
    m = MPI(merc_id, trxn_id)
    return m.KeySign(data)

@app.route('/sign_data', methods=['GET','POST'])
def sign_data():

    #print("---header---")
    #print(request.headers)
    
    print("------[sign_data]------")
    print(request.form)

    trans_type = "SALES"
    #trans_type = "INITRECURR"
    merc_id = app.config["MERCHANT_ID"]
    pan = request.form.get('MPI_PAN',"")
    cardholder_name = request.form.get('MPI_CARD_HOLDER_NAME',"")
    pan_exp = request.form.get('MPI_PAN_EXP',"")
    cvv2 = request.form.get('MPI_CVV2',"")
    trxn_id = request.form.get('MPI_TRXN_ID',"")
    puch_date = request.form.get('MPI_PURCH_DATE',"")
    purch_curr = "458"
    purch_amt = "1000"

    data = trans_type+merc_id+pan+cardholder_name+pan_exp+cvv2+trxn_id+puch_date+purch_curr+purch_amt
    print(data)
 
    m = MPI(merc_id, trxn_id, app.config['MPI_URL'])
    m.InitGw()
    return m.Sign(data)

@app.route('/mpi_status', methods=['POST','GET'])
def mpi_status():

    print("---header mpi_callback---")
    print(request.headers)
    
    print("------data mpi callback------")
    print(request.form)

    print("------result mpi callback------")
    result="OK"
    print(result)

    return Response(result, status=200)

@app.route('/mpi_redirect', methods=['POST', 'GET'])
def mpi_redirect():

    print("---mpi_redirect header---")
    print(request.headers)
    
    appr_code = request.form.get('MPI_APPR_CODE',"")
    rrn = request.form.get('MPI_RRN',"")
    bin = request.form.get('MPI_BIN',"")
    error_code = request.form.get('MPI_ERROR_CODE',"")
    error_desc = request.form.get('MPI_ERROR_DESC',"")
    merc_id = request.form.get('MPI_MERC_ID',"")
    trxn_id = request.form.get('MPI_TRXN_ID',"")
    mac = request.form.get('MPI_MAC',"")
    referral_code = request.form.get('MPI_REFERRAL_CODE',"")    
    
    # Additional data
    eci = request.form.get('MPI_ECI_VALUE',"")    
    challenge_mandated_ind = request.form.get('MPI_CHALLENGE_MANDATED_IND',"")    
    challenge_ind = request.form.get('MPI_CHALLENGE_IND',"")    
    auth_status = request.form.get('MPI_AUTH_STATUS',"")   
    status_reason = request.form.get('MPI_STATUS_REASON',"")   
    status_reason_desc = request.form.get('MPI_STATUS_REASON_DESC',"")
  
    #return Response(result, status=200)
    print("------render template------")
    return render_template('mpi-result.html', appr_code = appr_code, rrn = rrn, bin = bin, 
        error_code = error_code, error_desc = error_desc, merc_id = merc_id, trxn_id = trxn_id, 
        referral_code = referral_code,
        eci = eci, challenge_mandated_ind = challenge_mandated_ind, challenge_ind = challenge_ind,
        status_reason = status_reason, status_reason_desc = status_reason_desc,
        user = get_username(), is_admin=is_admin()
        )

#------------------------
# Proxy Helper functions
#------------------------

'''
@app.route('/redirect_proxy')
def redirect_proxy():

    a = is_admin()
    if a == 'N':
        if current_user.is_authenticated:
            flash(f'No access', category='danger')
            return redirect(url_for('devbox_getstarted'))
        else:
            form = LoginForm()
            flash(f'No access. Please login', category='warning')
            return redirect(url_for('login'))


    proxies = RedirectUrlProxy.query.limit(5).all()

    form = RedirectUrlProxyForm()
    return render_template('redirect-url-proxy.html', form = form, proxy = proxies, user = get_username(), is_admin=is_admin())

@app.route('/add_redirection_url', methods=['POST'])
def add_redirection_url():

    print("---header---")
    print(request.headers)

    print("------data------")
    print(request.form)
    
    proxy = RedirectUrlProxy()

    proxy.key = request.form.get('key',"")
    proxy.mid = request.form.get('mid',"")
    proxy.url = request.form.get('url',"")
    proxy.status_url = request.form.get('status_url',"")
    proxy.enable = request.form.get('enable',"")  
    proxy.user = current_user.get_id()

    db.session.add(proxy)
    db.session.commit()

    proxies = RedirectUrlProxy.query.all()
    form = RedirectUrlProxyForm()
    return render_template('redirect-url-proxy.html', form = form, proxy = proxies, user = get_username(), is_admin=is_admin())
    
@app.route('/toggle_redirection_url/<id>', methods=['GET'])
def toggle_redirection_url(id):
    print(f'Toggle redirection url id: {id}')
    proxy = RedirectUrlProxy.query.filter_by(id=id).first()
    if proxy != None:
        if proxy.enable == 'Y':
            proxy.enable = 'N'
        else:
            proxy.enable = 'Y'

        print(proxy)            
        db.session.add(proxy)
        db.session.commit()

    return redirect('/redirect_proxy')

@app.route('/update_redirection_url', methods=['POST'])
def update_redirection_url():

    print("---header---")
    print(request.headers)

    print("------data------")
    print(request.form)
    
    user = current_user.get_id()
    print(f"user = {user}")
    proxy = RedirectUrlProxy.query.filter_by(user = user).first()
    if proxy != None:      
        print(f"proxy = [{proxy}] ")     
        proxy.url = request.form.get('url',"")
        mid = proxy.mid
        db.session.commit()
        res = ws_merchant_update_url(mid, proxy.url)
        print(f"[{res}] update webservice")
        if res == "00":
            flash(f'Your redirection URL has been updated', category='success')
        else:
            flash(f'Unable to update the Redirection URL. Error={res}', category='danger')
        

    return redirect("/home")
'''


#------------------------
# Proxy functions
#------------------------

def _proxy_request(path, content_type):
    """Helper function to proxy requests to the MPI_URL."""
    url = app.config["MPI_URL"] + path
    print(f"Proxying request to: {url}")
    print("--- Request Headers ---")
    print(request.headers)

    # Determine data source based on content type
    request_data = request.data if 'json' in content_type else request.form
    print("--- Request Data ---")
    print(request_data)

    headers = {'Content-Type': content_type}
    
    try:
        r = requests.post(url, headers=headers, data=request_data, verify=False)
        print(f"--- Response: {r.status_code} ---")
        print(r.content)
        return Response(r.content, status=r.status_code)
    except Exception as e:
        error = str(e)
        print(f"--- Proxy Error --- \n{error}")
        return Response(error, status=500)

@app.route('/mpi/mkReq', methods=['GET', 'POST'])
def proxy_mkreq():
    return _proxy_request("/mkReq", 'application/json')

@app.route('/mpi/mpReq', methods=['GET', 'POST'])
def proxy_mpreq():
    return _proxy_request("/mpReq", 'application/x-www-form-urlencoded')

@app.route('/mpi/mercReq', methods=['GET', 'POST'])
def proxy_mercreq():
    return _proxy_request("/mercReq", 'application/x-www-form-urlencoded')

@app.route('/proxy/mpi_status', methods=['POST'])
def proxy_mpi_status():
    
    print("---header---")
    #print(request.headers)
    
    print("------data------")
    appr_code = request.form.get('MPI_APPR_CODE',"")
    rrn = request.form.get('MPI_RRN',"")
    bin = request.form.get('MPI_BIN',"")
    error_code = request.form.get('MPI_ERROR_CODE',"")
    error_desc = request.form.get('MPI_ERROR_DESC',"")
    merc_id = request.form.get('MPI_MERC_ID',"")
    trxn_id = request.form.get('MPI_TRXN_ID',"")
    mac = request.form.get('MPI_MAC',"")
    referral_code = request.form.get('MPI_REFERRAL_CODE',"")    
    
    # Additional data
    eci = request.form.get('MPI_ECI_VALUE',"")    
    challenge_mandated_ind = request.form.get('MPI_CHALLENGE_MANDATED_IND',"")    
    challenge_ind = request.form.get('MPI_CHALLENGE_IND',"")    
    auth_status = request.form.get('MPI_AUTH_STATUS',"")   
    status_reason = request.form.get('MPI_STATUS_REASON',"")   
    status_reason_desc = request.form.get('MPI_STATUS_REASON_DESC',"")
  
    try:
        key = trxn_id[0:2]
        print(f'Before Proxy : {key}')

        proxy = RedirectUrlProxy.query.filter_by(key=key, enable='Y', mid=merc_id).first()
        if proxy != None:

            print(proxy.url)
            # Need to overwrite the headers
            headers = { 
                'Content-Type' : 'application/x-www-form-urlencoded'
            }

            try:
                r = requests.post(proxy.status_url, headers = headers, data = request.form, verify=False)
                result=f"{r.status_code} {r.content}"
                print("------result [proxy.url]------")
                print(result)
                return Response(r.content, status=r.status_code)

            except Exception as e:
                error = str(e)
                result=error
                print("------result------")
                print(result)


    except Exception as e:
        print(str(e))
    
    return Response("OK", status=200)

@app.route('/proxy/mpi_redirect', methods=['POST'])
def proxy_mpi_redirect():
    
    print("---header---")
    #print(request.headers)
    
    print("------data------")
    appr_code = request.form.get('MPI_APPR_CODE',"")
    rrn = request.form.get('MPI_RRN',"")
    bin = request.form.get('MPI_BIN',"")
    error_code = request.form.get('MPI_ERROR_CODE',"")
    error_desc = request.form.get('MPI_ERROR_DESC',"")
    merc_id = request.form.get('MPI_MERC_ID',"")
    trxn_id = request.form.get('MPI_TRXN_ID',"")
    mac = request.form.get('MPI_MAC',"")
    referral_code = request.form.get('MPI_REFERRAL_CODE',"")    
    
    # Additional data
    eci = request.form.get('MPI_ECI_VALUE',"")    
    challenge_mandated_ind = request.form.get('MPI_CHALLENGE_MANDATED_IND',"")    
    challenge_ind = request.form.get('MPI_CHALLENGE_IND',"")    
    auth_status = request.form.get('MPI_AUTH_STATUS',"")   
    status_reason = request.form.get('MPI_STATUS_REASON',"")   
    status_reason_desc = request.form.get('MPI_STATUS_REASON_DESC',"")
  
    try:
        key = trxn_id[0:2]
        print(f'Before Proxy : {key}')

        proxy = RedirectUrlProxy.query.filter_by(key=key, enable='Y', mid=merc_id).first()
        if proxy != None:

            print(proxy.url)
            # Need to overwrite the headers
            headers = { 
                'Content-Type' : 'application/x-www-form-urlencoded'
            }

            try:
                r = requests.post(proxy.url, headers = headers, data = request.form, verify=False)
                result=f"{r.status_code} {r.content}"
                print("------result [proxy.url]------")
                print(result)
                return Response(r.content, status=r.status_code)

            except Exception as e:
                error = str(e)
                result=error
                print("------result------")
                print(result)


    except Exception as e:
        print(str(e))
    
    return render_template('mpi-result-default.html', appr_code = appr_code, rrn = rrn, bin = bin, 
        error_code = error_code, error_desc = error_desc, merc_id = merc_id, trxn_id = trxn_id, 
        referral_code = referral_code,
        eci = eci, challenge_mandated_ind = challenge_mandated_ind, challenge_ind = challenge_ind,
        status_reason = status_reason, status_reason_desc = status_reason_desc,
        #user=get_username(), is_admin=is_admin()
        user = get_username(), is_admin=is_admin()
        )

#------------------------
# Validate MAC functions
#------------------------

@app.route("/mac/upload_public_rsa", methods=['POST', 'GET'])
def upload_public_rsa():
    
    #u = current_user.get_id()
    #if u == None:
    #    u = 999999
    #print(f'u = {u}')

    print(request.files)
    '''myfile = request.files["public_rsa"]
    if myfile.filename != "":                
        key = myfile.read()
        print(f"== key: {key}" )

        mac_validate = MacValidateModel.query.filter_by(user=u).first()
        print(mac_validate)
        if mac_validate != None:
            mac_validate.public_rsa = key

            db.session.commit()
        else:
            mac_validate = MacValidateModel()
            mac_validate.user = u
            mac_validate.public_rsa = key

            db.session.add(mac_validate)
            db.session.commit()

    #flash(f'OK', category='success')
    return devbox_macvalidation(id="mac-validation")'''
    return "OK"

@app.route('/mac/upload_private_rsa', methods=['POST', 'GET'])
def upload_private_rsa():

    #u = current_user.get_id()
    #if u == None:
    #    u = 999999
    #print(f'u = {u}')

    '''myfile = request.files["private_rsa"]
    if myfile.filename != "":                
        key = myfile.read()
        print(f"== key: {key}" )

        mac_validate = MacValidateModel.query.filter_by(user=u).first()
        if mac_validate != None:
            print(f"found mac_validate for u={u}")

            print(mac_validate)

            mac_validate.private_rsa = key

            db.session.commit()
        else:
            print(f"NOT found mac_validate for u={u}")
            
            mac_validate = MacValidateModel()
            mac_validate.user = u
            mac_validate.private_rsa = key

            db.session.add(mac_validate)
            db.session.commit()

    #flash(f'OK', category='success')
    return redirect(url_for("devbox_macvalidation", id="mac-validation"))'''
    return "OK"

@app.route('/mac/generate_rsa', methods=['POST', 'GET'])
def generate_rsa():

    #u = current_user.get_id()
    #if u == None:
    #    u = 999999

    '''key = Key(u, u)
    key.GenKeys(save=False)

    mac_validate = MacValidateModel.query.filter_by(user=u).first()

    print("--------")
    print(mac_validate)
    print("--------")

    if mac_validate != None:
        mac_validate.private_rsa = key.privkey
        mac_validate.public_rsa = key.pubkey

        db.session.commit()
    else:
        mac_validate = MacValidateModel()
        mac_validate.user = u
        mac_validate.private_rsa = key.privkey
        mac_validate.public_rsa = key.pubkey

        db.session.add(mac_validate)
        db.session.commit()

    return redirect(url_for("devbox_macvalidation", id="mac-validation"))'''
    return "OK"

@app.route('/mac/validate', methods=['POST', 'GET'])
def mac_validate():

    #u = current_user.get_id()
    #if u == None:
    #    u = 999999

    '''print(request.form)
    # ImmutableMultiDict([('data', ''), ('mac', 'test'), ('sign_mac', 'Generate MAC Signature')])
    result = "Not Verified"
    data = request.form.get("data", "")
    signature = request.form.get("mac", "")
    if data == '':   
        flash(f'Please enter the data your wish to validate', category='warning')
        return redirect(url_for("devbox_macvalidation", id="mac-validation"))


    mac = MacValidateModel.query.filter_by(user=u).first()
    if mac == None:
        flash(f'Please upload your RSA keys or generate a new one',
              category='warning')
        return redirect(url_for("devbox_macvalidation", id="mac-validation"))
    if mac.private_rsa == "":
        flash(f'We could not detect the Private RSA Key. Click the upload button to upload it.', category='warning')
        return redirect(url_for("devbox_macvalidation", id="mac-validation"))
    if mac.public_rsa == "":
        flash(f'We could not detect the Public RSA Key. Click the upload button to upload it.', category='warning')
        return redirect(url_for("devbox_macvalidation", id="mac-validation"))
    

    public = mac.public_rsa
    private = mac.private_rsa
    key = Key(u, u)
    
    if request.form:
        if "sign_mac" in request.form:
            print(f'Click Sign MAC')
            if data == '':   
                flash(f'Please enter the data your wish to sign', category='warning')
                return redirect(url_for("devbox_macvalidation", id="mac-validation"))

            signature = key.Sign(data, private, public)
            print(f"The signature: {signature}")
            
            mac.data = data
            mac.mac = signature

            db.session.commit()

        else:
            print(f'Click verify')
            if data == '':   
                flash(f'Please enter the data your wish to validate', category='warning')
                return redirect(url_for("devbox_macvalidation", id="mac-validation"))
            if signature == '':   
                flash(f'Please enter the signature your wish to validate', category='warning')
                return redirect(url_for("devbox_macvalidation", id="mac-validation"))

            if key.IsValidSign(public, data, signature):
                result = "Verified"
            else:
                result = "Error"
            #print(f" Invalid: {isvalid}")

    form = MacValidateForm()
    form.public_rsa_key.data = public
    form.public_rsa_key.data = private
    form.data.data = data
    form.mac.data = signature

    #print(f"RESULT:{result}")
    redirect(url_for("devbox_macvalidation", id="mac-signature"))
    return render_template('api-mac-validation.html', scrollToAnchor='mac-signature', 
    result=result, form=form, public=public, private=private, user = get_username(), is_admin=is_admin())'''
    return "OK"

#------------------------
# WEB SERVICES
#------------------------



#------------------------
# PING
#------------------------

@app.route('/ping', methods=['GET', 'POST'])
def ping():    
    return "pong"

@app.route('/pong',)
def pong():
    print("---header---")
    print(request.headers)
    
    print("------data------")
    request_data = request.get_json()
    print(request_data)

    return "ping"