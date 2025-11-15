import requests, os, random
from project import app, czws, db, bcrypt, mail
from datetime import date, time, datetime, timedelta
from flask import current_app, render_template, redirect, url_for, flash, request, send_file, send_from_directory, safe_join, abort, Response
from flask_login import login_user, logout_user, current_user, login_required
from flask_mail import Message
from project.forms import LoginForm, RegistrationForm, MpiForm, RedirectUrlProxyForm, LiveEnvForm, MacValidateForm, ChangePasswordForm, ForgotPasswordForm
from project.models import User, RedirectUrlProxy, LiveEnv, MacValidateModel
from project.mpi import MPI
from project.key import Key
from project.CZWebService import CZWebService

# ---------------------
# OpenAPI Implementation
# ---------------------

@app.route('/devbox', defaults={'module': "sales_v2_4"})
@app.route('/devbox/<module>')
def devbox(module):
    
    module = module + ".json"
    print(module)
    return render_template('devbox.html', module=module, title="Dev Box", user=get_username(), is_admin=is_admin())


# ---------------------
# Authen Only Implementation
# ---------------------
#@app.route('/auth')
#def auth_only():
#    now = datetime.now().strftime("%Y%m%d%H%M%S")
#
#    # Load default value
#    form = MpiForm()
#    form.MPI_TRXN_ID.data       = 'dev' + now
#    form.MPI_PURCH_DATE.data 	= now
#    return render_template('auth.html', form=form, user=get_username(), is_admin=is_admin())


#@app.route("/anonhosted", methods=['GET','POST'])
#def anonhosted_iframe():
#    now = datetime.now().strftime("%Y%m%d%H%M%S")
#
#    # Load default value
#    form = MpiForm()
#    form.MPI_TRXN_ID.data       = 'dev' + now
#    form.MPI_PURCH_DATE.data 	= now
#    return render_template('ianonhosted.html', form=form, user=get_username(), is_admin=is_admin())    


# ---------------------
# DevBox Implementation
# ---------------------

@app.route('/home', methods=['GET', 'POST'])
@app.route('/', methods=['GET', 'POST'])
@app.route('/api/get-started')
def devbox_getstarted():
    
    # 20211220 : Login First
    #if not current_user.is_authenticated:
    #    return redirect(url_for('login'))
    # End

    proxyform = LiveEnvForm() 

    is_login = 'N'
    live_now = is_live()

    if current_user.is_authenticated:
        u = current_user.get_id()
        is_login = 'Y'

        # Get proxy detail #1
        proxy = RedirectUrlProxy.query.filter_by(user = u).first()
        if proxy != None:           
            proxyform.mid.data = proxy.mid
            proxyform.mProxyKey.data = proxy.key
            proxyform.url.data = proxy.url
            proxyform.status_url.data = proxy.status_url 
        else:  
            proxyform.mid.data = app.config['TEST1_MID']


    return render_template('api-started.html', is_login=is_login, 
        proxyform=proxyform, user=get_username(), is_admin=is_admin())

@app.route('/api/sales-flow')
def devbox_sales_flow():

    # 20211220 : Login First
    #if not current_user.is_authenticated:
    #    return redirect(url_for('login'))
    # End

    a = is_admin()
    name = get_username()
    return render_template('api-sales-flow.html', is_admin=a, user=name)

@app.route('/api/checkout')
def devbox_checkout():

    # 20211220 : Login First
    #if not current_user.is_authenticated:
    #    return redirect(url_for('login'))
    # End

    a = is_admin()
    
    return render_template('api-checkout.html', is_admin=a, user=get_username())

#@app.route('/api/message-type')
#def devbox_messagetype():
#
#    # 20211220 : Login First
#    if not current_user.is_authenticated:
#        return redirect(url_for('login'))
#    # End
#
#    a = is_admin()
#    
#    return render_template('api-message-type.html', is_admin=a, user=get_username())

@app.route('/api/mac-validation/<id>')
@app.route('/api/mac-validation', defaults={'id': "mac-process"})
def devbox_macvalidation(id):
    
    # 20211220 : Login First
    #if not current_user.is_authenticated:
    #    return redirect(url_for('login'))
    # End
        
    a = is_admin()

    public=""
    private=""
    result="Unverified"
    form = MacValidateForm()

    u = current_user.get_id()
    if u == None:
        u = 999999

    mac = MacValidateModel.query.filter_by(user=u).first()
    if mac != None:
        public = mac.public_rsa
        private = mac.private_rsa

    return render_template('api-mac-validation.html', id=id, result=result, form=form, 
    public=public, private=private, user=get_username(), is_admin=is_admin())

# ---------------------
# Standard Navigation
# ---------------------

@app.route('/logout', methods=['GET','POST'])
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/login', methods=['POST','GET'])
def login():
    
    if current_user.is_authenticated:
        #audit('Login()', "User is authenticated")
        return redirect(url_for('devbox_getstarted'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            flash(f'Successfully login', category='success')
            audit("Login()", "User successfully login")

            if user.is_reset == 1:
                return redirect(url_for('change_password'))

            return redirect(url_for("devbox_getstarted"))
        else:
            flash(f'Failed to login', category='danger')
            audit("Login()", "User failed login")
            return redirect(url_for('login'))
    return render_template('login.html', title="Login", form=form, user=get_username(), is_admin=is_admin())

@app.route('/register', methods=['POST', 'GET'])
def register():
    #if current_user.is_authenticated:
    #    return redirect(url_for('devbox_getstarted'))

    a = is_admin()
    if a == 'N':
        if current_user.is_authenticated:
            flash(f'No access', category='danger')
            return redirect(url_for('devbox_getstarted'))
        else:
            form = LoginForm()
            flash(f'No access. Please login', category='warning')
            return redirect(url_for('login'))

    #id = current_user.get_id()
    #print(id)
    #try:
    #    user = User.query.filter_by(id=id).first()
    #    print(user)
    #    if user.is_admin == 'N':
    #        return redirect(url_for('devbox_getstarted'))
    #except:
    #    audit("register", "No Permission")
    #    return redirect(url_for('devbox_getstarted'))


    form = RegistrationForm()
    if form.validate_on_submit():

        # 01. Insert user into database
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            flash(f'Account with this email has already exist {form.email.data}', category='warning')
            return render_template('register.html', title="Register", form=form, user=get_username(), is_admin=is_admin())

        encrypted_password = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        user = User(username=form.username.data,
                    email=form.email.data, password=encrypted_password,
                    organization=form.organization.data)
        user.is_reset = 1
        db.session.add(user)
        db.session.commit()
        
        # 02. Insert MID into database
        proxy = RedirectUrlProxy()
        proxy.user = user.id
        proxy.mid = form.mid.data
        proxy.enable = 'Y'
        proxy.status_url
        proxy.url = "https://mpidevbox-do7t.onrender.com/proxy/mpi_redirect"
        proxy.status_url = ""
        proxy.key = "AA"
        db.session.add(proxy)
        db.session.commit()

        # 03. Send Email
        url = app.config['LOGIN_LINK']

        req = f'Hi {user.username},' + "\n\n"
        req = req + f"Welcome to Paydee developer portal." + "\n\n"
        req = req + f"Here is your login detail." + "\n"
        req = req + f"  Login(Email): {user.email}" + "\n"
        req = req + f"  Password: {form.password.data}" + "\n\n"
        req = req + f"Please click the link below to login and change your password immediately." + "\n\n"
        req = req + f"  {url}\n\n"
        req = req + f"Regards," + "\n"
        req = req + f"Paydee Team" 

        msg = Message("Welcome to Paydee",
                    sender="no_reply@paydee.co",
                    recipients=[user.email])
                    #,
                    #bcc=[app.config['GOLIVE_TEAM_EMAIL']])
        msg.body = req
        mail.send(msg)

        audit('Register()', f'Account created successfully for User:{form.username.data} Email:{form.email.data}')
        flash(f'Account created successafully for {form.username.data}', category='success')
        return redirect(url_for("login"))
    return render_template('register.html', title="Register", form=form, user=get_username(), is_admin=is_admin())

@app.route('/change_password', methods=['POST', 'GET'])
def change_password():

    form = ChangePasswordForm()
    if form.validate_on_submit():

        user = User.query.filter_by(id=current_user.get_id()).first()
        if user:
            encrypted_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            user.password=encrypted_password
            user.is_reset = 0
            db.session.commit()
            flash(f'Your password has been updated', category='success')
        else:
            flash(f'Failed to change password', category='danger')
            return redirect(url_for('login'))

        return redirect(url_for('change_password'))
    return render_template('change_password.html', title="Login", form=form, user=get_username(), is_admin=is_admin())

@app.route('/reset_password', methods=['POST', 'GET'])
def forgot_password():

    form = ForgotPasswordForm()
    if form.validate_on_submit():

        user = User.query.filter_by(email=form.email.data).first()

        if user:

            pwd = ''.join((random.choice('abcdxyzpqr!@#$_120974') for i in range(6)))
            encrypted_password = bcrypt.generate_password_hash(pwd).decode('utf-8')
            user.password=encrypted_password
            user.is_reset = 1
            db.session.commit()

            url = app.config['LOGIN_LINK']

            req = f'Greetings from Paydee,' + "\n\n"
            req = req + f"We received a request to reset password." + "\n"
            req = req + f"Here is your new password: {pwd}" + "\n"
            req = req + f"Please click the link below to login and change your password immediately." + "\n\n"
            req = req + f"  {url}\n\n"
            req = req + f"Regards," + "\n"
            req = req + f"Paydee Team" 

            msg = Message("Paydee Password Reset Service",
                        sender="no_reply@paydee.co",
                        recipients=[user.email])
                        #bcc=[app.config['GOLIVE_TEAM_EMAIL']])
            msg.body = req
            mail.send(msg)

        flash(f'We have email you the instruction to reset your password.', category='success')
        return redirect(url_for('login'))
    return render_template('forgot_password.html', title="Login", form=form, user=get_username(), is_admin=is_admin())


# ---------------------
# Helper Function
# ---------------------

def audit(function_name, action):
    #t = time.strftime("%Y%m%d %H%M%S")

    if current_user.is_authenticated:
        u = current_user.get_id()
    else:
        u = 0

    print( f"[][{u}] {function_name} {action}" )
    #audit = Audit(user_id=u, activity=f"{function_name} {action}")
    #db.session.add(audit)
    #db.session.commit()
    
def is_admin():
    
    admin = 'N'

    if current_user.is_authenticated:
        u = current_user.get_id()
        user = User.query.filter_by(id=u).first()
        if user != None:
            admin = user.is_admin

    return admin

def is_live():

    live = 'N'

    if current_user.is_authenticated:
        u = current_user.get_id()
        env = LiveEnv.query.filter_by(user=u).first()
        if env != None:
            live = env.enable

    return live

def get_username():
    admin = 'Anon'

    if current_user.is_authenticated:
        u = current_user.get_id()
        user = User.query.filter_by(id=u).first()
        if user != None:
            admin = "Welcome back, " + user.username

    return admin

@app.route("/download/<name>")
def download(name):
    dir = os.path.join(current_app.root_path, app.config['UPLOAD_FOLDER'])
    print(dir)
    try:
        return send_from_directory(directory=dir, filename=name, as_attachment=True)
    except FileNotFoundError:
        abort(404)

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


#------------------------
# Environments
#------------------------

@app.route('/add_proxy', methods=['POST'])
@app.route('/add_test_environment', methods=['POST'])
def add_test_environment():
    print("---header---")
    print(request.headers)
    
    print("------data------")
    #print(request.form)
    mid = request.form.get('mid',"")
    proxy_key = request.form.get('mProxyKey',"")
    url = request.form.get('url',"")
    status_url = request.form.get('status_url',"")
    u = current_user.get_id()

    # Now update the database
    dbproxy = RedirectUrlProxy.query.filter_by(user=u, mid=mid).first()
    if dbproxy != None:
        dbproxy.key = proxy_key
        dbproxy.url = url
        dbproxy.status_url = status_url
        dbproxy.enable = 'Y'

        db.session.commit()

        flash(f'Your test environment has been updated', category='success')
    else:
        dbproxy = RedirectUrlProxy()
        
        dbproxy.user = u
        dbproxy.mid = mid
        dbproxy.key = proxy_key
        dbproxy.url = url
        dbproxy.status_url = status_url
        dbproxy.enable = 'Y'

        db.session.add(dbproxy)
        db.session.commit()

        flash(f'Your test environment has been setup', category='success')

    return redirect(url_for('devbox_getstarted'))

@app.route('/add_live_environment', methods=['POST'])
def add_live_environment():

    u = current_user.get_id()
    user = User.query.filter_by(id=u).first()

    print('===add_live_environment---')
    #print(request.form)
    mid = request.form.get('mid',"")
    url = request.form.get('url',"")
    status_url = request.form.get('status_url',"")
    key = ""

    myfile = request.files["rsa_key"]
    if myfile.filename != "":                
        key = myfile.read()
        print(f"== key: {key}" )

    # Insert into database
    liveenv = LiveEnv()
    
    liveenv.user = u
    liveenv.mid = mid
    liveenv.url = url
    liveenv.status_url = status_url
    liveenv.public = key
    liveenv.enable = 'U'
    liveenv.organization = user.organization
    
    db.session.add(liveenv)
    db.session.commit()

    flash(f'Your live environment has been updated', category='success')
    return redirect('/api/get-started')

@app.route('/go_live', methods=['POST', 'GET'])
def go_live():

    now = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

    u = current_user.get_id()
    user = User.query.filter_by(id=u).first()
    liveenv = LiveEnv.query.filter_by(user = u).first() 
    
    # Sanity checks
    if liveenv == None:
        flash(f'Please setup your live environment data', category='danger')
        return redirect('/api/get-started')

    if liveenv.url == "":
        flash(f'Please setup your Event Webhook', category='danger')
        return redirect('/api/get-started')

    req = f'Request: GO LIVE \n'
    req = req + f'Date: {now} \n'
    req = req + f'User: {user.username}\n'
    req = req + f'Organization : {user.organization}\n'
    req = req + f'MID: {liveenv.mid}\n'
    req = req + f'URL: {liveenv.url}\n'
    req = req + f'Status URL: {liveenv.status_url}\n'
    req = req + f'Public Key: {liveenv.public}'

    msg = Message("Request: Go Live",
                  sender="bot@paydee.co",
                  recipients=[app.config['GOLIVE_TEAM_EMAIL']])
    msg.body = req
    mail.send(msg)

    flash(f'Our team has been notified and will review your go-live request. The review process should not take more than 24 hours.', category='success')
    return redirect('/api/get-started')

@app.route('/go_live/<id>', methods=['POST'])
def update_go_live(id):

    print("------data------")
    print(request.headers)
    print(request.form)
    mid = request.form.get('MID',"")
    if mid == "":
        flash(f'Oops! Could not detect the Merchant ID.', category='danger')
        return redirect('/live_environment')

    live = LiveEnv.query.filter_by(user=id).first()
    if live == "":
        flash(f'Oops! Could not find user id {id}', category='danger')
        return redirect('/live_environment')

    live.enable = 'Y'
    live.mid = mid

    db.session.commit()

    flash(f'Good job!', category='success')
    return redirect('/live_environment')

@app.route('/live_environment', methods=['POST', 'GET'])
def live_environment():

    a = is_admin()
    if a == 'N':
        if current_user.is_authenticated:
            flash(f'No access', category='danger')
            return redirect(url_for('devbox_getstarted'))
        else:
            form = LoginForm()
            flash(f'No access. Please login', category='warning')
            return redirect(url_for('login'))

    lives = LiveEnv.query.all()

    return render_template('live-environment.html', lives=lives, user=get_username(), is_admin=is_admin())

#------------------------
# Proxy functions
#------------------------

@app.route('/mpi/mkReq', methods=['GET', 'POST'])
def proxy_mkreq():

#    result="OK"
#    return Response(result, status=200)

    url = app.config["MPI_URL"] + "/mkReq"
    r=""

    print("---header---")
    print(request.headers)

    # Need to overwrite the headers
    headers = { 
        'Content-Type' : 'application/json'
    }

    print("------data------")
    print(request.data)

    try:
        r = requests.post(url, headers = headers, data = request.data, verify=False)
        result=f"{r.status_code} {r.content}"
        print("------result------")
        print(result)
        return Response(r.content, status=r.status_code)

    except Exception as e:
        error = str(e)
        result=error
        print("------result------")
        print(result)

    return Response(result, status=200)

@app.route('/mpi/mpReq', methods=['GET', 'POST'])
def proxy_mpreq():
    url = app.config["MPI_URL"] + "/mpReq"
    #url="http://localhost:5000/mpi_status"
    r=""

    print("---header---")
    print(request.headers)

    print("------data------")
    print(request.form)

    # Need to overwrite the headers
    headers = { 
        'Content-Type' : 'application/x-www-form-urlencoded'
    }

    try:
        r = requests.post(url, headers = headers, data = request.form, verify=False)
        result=f"{r.status_code} {r.content}"
        print("------result------")
        print(result)
        return Response(r.content, status=r.status_code)

    except Exception as e:
        error = str(e)
        result=error
        print("------result------")
        print(result)

    return Response(result, status=200)

@app.route('/mpi/mercReq', methods=['GET', 'POST'])
def proxy_mercreq():
    url = app.config["MPI_URL"] + "/mercReq"
    #url="http://localhost:5000/mpi_status"
    r=""

    print("---header---")
    print(request.headers)

    print("------data------")
    print(request.form)

    # Need to overwrite the headers
    headers = { 
        'Content-Type' : 'application/x-www-form-urlencoded'
    }

    try:
        r = requests.post(url, headers = headers, data = request.form, verify=False)
        result=f"{r.status_code} {r.content}"
        print("------result------")
        print(result)
        return Response(r.content, status=r.status_code)

    except Exception as e:
        error = str(e)
        result=error
        print("------result------")
        print(result)

    return Response(result, status=200)

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
        user = get_username(), is_admin=is_admin()
        )

#------------------------
# Validate MAC functions
#------------------------

@app.route("/mac/upload_public_rsa", methods=['POST', 'GET'])
def upload_public_rsa():
    
    u = current_user.get_id()
    if u == None:
        u = 999999
    print(f'u = {u}')

    print(request.files)
    myfile = request.files["public_rsa"]
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
    return devbox_macvalidation(id="mac-validation")

@app.route('/mac/upload_private_rsa', methods=['POST', 'GET'])
def upload_private_rsa():

    u = current_user.get_id()
    if u == None:
        u = 999999
    print(f'u = {u}')

    myfile = request.files["private_rsa"]
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
    return redirect(url_for("devbox_macvalidation", id="mac-validation"))

@app.route('/mac/generate_rsa', methods=['POST', 'GET'])
def generate_rsa():

    u = current_user.get_id()
    if u == None:
        u = 999999

    key = Key(u, u)
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

    return redirect(url_for("devbox_macvalidation", id="mac-validation"))

@app.route('/mac/validate', methods=['POST', 'GET'])
def mac_validate():

    u = current_user.get_id()
    if u == None:
        u = 999999

    print(request.form)
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
    result=result, form=form, public=public, private=private, user = get_username(), is_admin=is_admin())

#------------------------
# WEB SERVICES
#------------------------

@app.route('/merchant_update_url', methods=['POST', 'GET'])
def ws_merchant_update_url(mid, threed_url, status_url=""):
  
    
    res = czws.merchant_update_url(mid=mid, threed_url=threed_url, status_url=status_url)
    return res

@app.route('/ws_login', methods=['POST', 'GET'])
def ws_login():
    #ws = CZWebService(base_url="https://33faa306-47f0-412d-8d72-22e7aadfda6b.mock.pstmn.io")
    #ws = CZWebService()
    #res = ws.login()
    #res = czws.login()
    threed_url = "https://mpidevbox-do7t.onrender.com/proxy/mpi_redirect"
    status_url = "https://mpidevbox-do7t.onrender.com/proxy/mpi_status"
    threed_url = "https://mpidevbox-do7t.onrender.com/proxy/threed_url"
    status_url = "https://mpidevbox-do7t.onrender.com/proxy/status_url"    
    res = czws.merchant_update_url(mid="000000000000051", threed_url=threed_url, status_url=status_url)
    print(res)
    #res = czws.merchant_inq(mid="000000000000033")
    return res

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