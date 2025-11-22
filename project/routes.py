import requests, os, random
from project import app, mail
from datetime import date, time, datetime, timedelta
from flask import current_app, render_template, redirect, url_for, flash, request, send_file, send_from_directory,  abort, Response, session
from flask_mail import Message
from project.forms import MpiForm
from project.mpi import MPI
from project.key import Key


@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('index.html')

# ---------------------
# MPI Function
# ---------------------    


#------------------------
# Proxy functions
#------------------------

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

