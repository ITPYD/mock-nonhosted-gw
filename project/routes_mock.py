import requests, os, random
from project import app
from datetime import date, time, datetime, timedelta
from flask import current_app, render_template, redirect, url_for, flash, request, send_file, send_from_directory, abort, Response, Flask, jsonify
from werkzeug.utils import safe_join # This import should now be resolved
import json # You'll need this import if not already present


import project.routes
from project.mpi import MPI
from project.key import Key


#------------------------
# CORE PROXY FUNCTION
#------------------------
def _proxy_request(path, content_type, prefix=""):
    """Helper function to proxy requests (POST/GET) to the MPI_URL."""

    # Using mock_app.config for demonstration, replace with app.config in production
    url = mock_app.config["MPIGW_URL"] + path
    print(f"-----{prefix}: {path[1:]}---------")
    print(f"Proxying request to: {url}")
    
    # Determine which data source to use based on content type
    if 'json' in content_type:
        # In a real app: request_data = request.data
        request_data = b'{"mock": "data"}' 
        data_to_send = request_data
    else:
        # In a real app: request_data = request.form
        request_data = request.form # Get actual form data from the incoming request
        data_to_send = request_data
        
    headers = {'Content-Type': content_type}
    method = request.method.upper()

    try:
        # NOTE: The actual 'requests' library call is replaced with a mock 
        # to ensure the file remains self-contained and runnable.
        
        # r = requests.post(url, headers=headers, data=data_to_send, verify=False, timeout=30)
        # r_status_code = r.status_code
        # response_content = r.content
        
        # --- MOCKING A SUCCESSFUL requests RESPONSE ---
        r_status_code = 200
        response_content = b'MOCK: Transaction Registered Successfully'
        
        if path == "/mercReq":
            print("--- DEBUG: FULL CONTENT FOR /mercReq RESPONSE ---")
            print(response_content.decode('utf-8', errors='ignore'))
            print("-----------------------------------------------")

        # ... (omitting Cross-Origin/Webhook Fix logic for brevity) ...

        print(f"--- Response: {r_status_code} ---")
        # Return the Flask Response object
        return Response(response_content, status=r_status_code)
        
    except Exception as e:
        error = str(e)
        print(f"--- Proxy Error --- \n{error}")
        return Response(error, status=500)


#------------------------
# MOCK ROUTES (API ENDPOINTS)
#------------------------


def _custom_proxy_request(path, data, prefix):
    """Helper function for the final initiation request using a custom payload."""
    url = mock_app.config["MPIGW_URL"] + "/" + path
    print(f"*** {prefix}: Proxying final request to: {url}")

    try:
        # NOTE: requests.post call is mocked here.
        
        # r = requests.post(url, data=data, verify=False, timeout=30)
        # return Response(r.content, status=r.status_code, mimetype=r.headers.get('Content-Type', 'text/html'))
        
        # --- MOCKING A SUCCESSFUL FINAL REDIRECT RESPONSE ---
        html_content = f"<html><body><p>Mock Payment Redirect for {path.split('/')[-1].upper()}</p><p>Channel: {data.get('PAG_CHANNEL_NAME')}</p></body></html>"
        return Response(html_content, status=200, mimetype='text/html')
        
    except Exception as e:
        error = str(e)
        print(f"*** Custom Proxy Error --- \n{error}")
        return Response(error, status=500)


# --- UPDATED /mock/mpReq ROUTE ---
@app.route('/pag/mpReq', methods=['GET', 'POST'])
@app.route('/mock/mpReq', methods=['GET', 'POST'])
def mock_mpreq():
    """
    Handles the mock flow: 
    1. Proxies mercReq (transaction registration) using original data.
    2. Assumes success and constructs a new payload for fpx/init.
    3. Proxies the fpx/init request using the custom payload and returns the final response.
    """
    print(f" ==== mpReq === \n")
    

    original_data = dict(request.form)
    # Get the payment channel ID and standardize it for comparison
    channel_id = original_data.get('MPI_PAYMENT_CHANNEL_ID', 'Public Bank').upper()
    if channel_id in ('BOOST', 'GRABPAY', 'TNG-EWALLET', 'MB2U_QRPAY-PUSH', 'SHOPEEPAY', 'ALIPAY', 'GUPOP'):
        target_endpoint_path = "mpigw/wallet/init"
    else:
        target_endpoint_path = "mpigw/fpx/init"


    ret = _proxy_request("/mercReq", 'application/x-www-form-urlencoded', prefix="mock")
    # Check the result of the mercReq proxy call (New requirement implemented here)
    if ret.get('status') != 200:
        print(f"ERROR: mercReq failed with response: {ret}")
        # Fail early and return an error response
        # In a real app, you would render a user-friendly error page.
        error_message = ret.get('message', 'Transaction registration failed due to unknown error.')
        return f"Transaction Registration Failed: {error_message}", 500

    # 3. Construct the data payload for fpx/init
    # This payload is for the second request, which initiates the bank selection screen.
    fpx_data_payload = {
        # Copied/Derived from the incoming request (mercReq)
        "PAG_MERCHANT_ID": original_data.get('MPI_MERC_ID', '000000000000033'),
        "PAG_CUST_EMAIL": original_data.get('MPI_EMAIL', 'test@example.com'),
        "PAG_TRANS_ID": original_data.get('MPI_TRXN_ID', 'mdl_default_id'),
        "PAG_CHANNEL_NAME": channel_id,
        "PAG_ORDER_DETAIL": "PAG Merchant Order",
        "PAG_MAC": "Some-Random-MAC-String-For-FPX", # Placeholder MAC for FPX
    }
    
    return _custom_proxy_request(target_endpoint_path, fpx_data_payload, prefix="mock")

# 
@app.route('/pag/mercReq', methods=['GET', 'POST'])
@app.route('/mock/mercReq', methods=['GET', 'POST'])
def mock_mercreq():
    return _proxy_request("/mercReq", 'application/x-www-form-urlencoded', prefix="mock")

# The route that returns the HTML form
@app.route('/pag/mkReq', methods=['GET', 'POST'])
@app.route('/mock/mkReq', methods=['GET', 'POST'])
def mock_mkreq():
    print("debug")
    # Note: Ensure the path casing here matches the remote API
    return _proxy_request("/mkReq", 'application/json', prefix="mock")

# NEW: Route to handle the form submission action "cardReq"
@app.route('/pag/cardReq', methods=['POST'])
@app.route('/mock/cardReq', methods=['POST'])
def mock_card_req():
    """Handles the form submission from the proxied HTML page."""
    # This route intercepts the POST from the HTML form and proxies it to the remote API
    return _proxy_request("/cardReq", 'application/x-www-form-urlencoded', prefix="mock")

@app.route('/pag/maReq', methods=['POST'])
@app.route('/mock/maReq', methods=['POST'])
def mock_mareq():
    """Handles the form submission action 'maReq' and proxies it to the remote MPI."""
    # This request contains the final browser info and is a standard form submission.
    return _proxy_request("/maReq", 'application/x-www-form-urlencoded', prefix="mock")

@app.route('/pag/notifyReq', methods=['POST'])
@app.route('/mock/notifyReq', methods=['POST'])
def mock_notify_req():
    """Handles the final form submission from the 3DS iFrame and proxies it."""
    # This request should be proxied back to the remote MPI server to complete the 3DS flow.
    return _proxy_request("/notifyReq", 'application/x-www-form-urlencoded', prefix="mock")


@app.route('/pag/channels', methods=['POST', 'GET'])
@app.route('/mock/channels', methods=['POST', 'GET'])
def mock_channels():
    """
    Mocks the /channels endpoint, returning a list of available payment channels.
    This simulates the response structure where a merchant fetches options.
    """
    print("-----mock: channels---------")
    print("Returning mocked payment channels.")
    
    # --- Sample Data Structure (Adjust as needed) ---
    # This structure is highly typical for payment method lists.
    response_data = {
        "MPI_ERROR_CODE": "000",
        "MPI_ERROR_DESC": "SUCCESS",
        "MPI_CHANNEL_LIST": [
            {
                "MPI_PAYMENT_METHOD": "FPX",
                "MPI_PAYMENT_CHANNEL": ["PUBLIC_BANK=A", "ALRAJHI=A", "MAYBANK=B"]
            }
        ]
    }
    
    # Return the data as a JSON response with status 200
    return jsonify(response_data), 200

# Optionally, you might want to call your existing proxy helper
# to simulate how a real request would flow through your mock server
# if the client expects a proxied response. 
# If the client is calling /mock/channels directly, the jsonify method is better.

#------------------------
# STATIC RESOURCE PROXY (CRITICAL FIX FOR CSS/JS/IMAGES)
#------------------------

# In your routes_mock.py
#------------------------
# CORE PROXY FUNCTION (Finalized with all URL replacements)
#------------------------

@app.route('/pag/3ds/<path:subpath>', methods=['GET', 'POST'])
@app.route('/mock/3ds/<path:subpath>', methods=['GET', 'POST'])
def mock_3ds_proxy(subpath):
    """Proxies 3DS content (callback/mon) and patches URLs to bypass CORS."""
    
    base_3ds_url = 'https://paydee-test.as1.gpayments.net'
    remote_url = f"{base_3ds_url}/{subpath}"
    
    print(f"--- 3DS PROXY: Fetching {remote_url} ---")
    print(f"--- 3DS PROXY: Request args {request.args} ---")

    # CRITICAL FIX: Extract essential headers from the browser's request
    # We copy all headers except ones that might interfere with requests (like Host, Content-Length)
    # The dictionary comprehension copies headers while excluding problematic ones.
    proxied_headers = {
        key: value 
        for key, value in request.headers.items() 
        if key.lower() not in ['host', 'content-length', 'connection']
    }
    
    try:
        # 1. Execute the request to the remote 3DS server
        if request.method == 'POST':
            # FIX 1: Pass the captured headers
            # FIX 2: Pass the query parameters via 'params'
            resp = requests.post(remote_url, 
                                 headers=proxied_headers,
                                 params=request.args,  # <--- CRITICAL: Forwards transId, did
                                 data=request.data,    # Forwards browser info form data
                                 verify=True, timeout=30)
        else: # GET request
            resp = requests.get(remote_url, 
                                headers=proxied_headers,
                                params=request.args, 
                                verify=True, timeout=30)
        response_content = resp.content
        

        #print(f"--- 3DS PROXY RESPONSE CONTENT ({subpath}): {resp.content.decode('utf-8', errors='ignore')}")
        #print(f"--- 3DS PROXY: Response Status: {resp.status_code} ---")

        # 2. Apply the URL Patching (keeping this active as confirmed necessary)
        REMOTE_3DS_PREFIX = b'https://paydee-test.as1.gpayments.net'
        LOCAL_3DS_PREFIX = b'/mock/3ds'
        
        # if REMOTE_3DS_PREFIX in response_content:
        #     print(f"--- 3DS PROXY PATCH APPLIED: {subpath} ---")
        #     response_content = response_content.replace(REMOTE_3DS_PREFIX, LOCAL_3DS_PREFIX)

        # NEW: The final MPI domain to be patched
        REMOTE_MPI_DOMAIN = b'https://devlink.paydee.co/mpi/notifyReq'
        LOCAL_NOTIFY_PATH = b'/mock/notifyReq' # Create this new route

        # CRITICAL NEW PATCHING STEP: Handle the final form action URL
        # if REMOTE_MPI_DOMAIN in response_content:
        #     print(f"--- 3DS PROXY PATCH APPLIED (MPI domain): {subpath} ---")
        #     response_content = response_content.replace(REMOTE_MPI_DOMAIN, LOCAL_NOTIFY_PATH)


        # WEBHOOK
        DEFAULT_WEBHOOK = b'https://devlinkv2.paydee.co/mpigw/mpi/payment-status/redirect'
        LOCAL_WEBHOOK = b'https://devlinkv2.paydee.co/mpigw/payment/status'

        # if DEFAULT_WEBHOOK in response_content:
        #     print(f"--- DEFAULT WEBHOOK PATCH APPLIED ---")
        #     response_content = response_content.replace(DEFAULT_WEBHOOK, LOCAL_WEBHOOK)

        # 3. Return the patched content with all original response headers
        return Response(response_content, status=resp.status_code, headers=resp.headers)
        
    except Exception as e:
        error = str(e)
        print(f"--- 3DS Proxy Error: {error} ---")
        return f"Error proxying 3DS: {e}", 500

@app.route('/mpigw/<path:filename>', methods=['GET', 'POST'])
def mock_js_proxy(filename):
    """Proxies requests for static assets (CSS, JS, Images) back to the remote server."""
    
    mpi_url = app.config['MPIGW_URL']
    remote_url = f"{mpi_url}/{filename}"
    
    print(f"--- RESOURCE PROXY: Fetching {remote_url} ---")
    
    try:
        # Use the request method from the client for the proxy request
        if request.method == 'POST':
            resp = requests.post(remote_url, data=request.data, verify=True)
        else:
            resp = requests.get(remote_url, verify=True, timeout=30)
            
        print(f"--- RESOURCE PROXY: Response Status: {resp.status_code} ---")
        print(f"--- RESOURCE PROXY: Response Content-Type: {resp.headers.get('Content-Type')} ---")


        response_content = resp.content
        # # WEBHOOK
        # DEFAULT_WEBHOOK = b'https://devlinkv2.paydee.co/mpigw/mpi/payment-status/redirect'
        # LOCAL_WEBHOOK = b'https://devlinkv2.paydee.co/mpigw/payment/status'

        # if DEFAULT_WEBHOOK in response_content:
        #     print(f"--- DEFAULT WEBHOOK PATCH APPLIED ---")
        #     response_content = response_content.replace(DEFAULT_WEBHOOK, LOCAL_WEBHOOK)

        # Return the content directly, ensuring correct MIME type is passed
        return response_content, resp.status_code, {'Content-Type': resp.headers['Content-Type']}
        
    except Exception as e:
        error = str(e)
        print(f"--- Resource Proxy Error: {error} ---")
        return f"Error proxying resource: {e}", 500



@app.route('/pag/resources/<path:filename>', methods=['GET', 'POST'])
@app.route('/mpi/resources/<path:filename>', methods=['GET', 'POST'])
@app.route('/mock/resources/<path:filename>', methods=['GET', 'POST'])
def mock_resource_proxy(filename):
    """Proxies requests for static assets (CSS, JS, Images) back to the remote server."""
    
    mpi_url = app.config['MPI_URL']
    remote_url = f"{mpi_url}/resources/{filename}"
    
    print(f"--- RESOURCE PROXY: Fetching {remote_url} ---")
    
    try:
        # Use the request method from the client for the proxy request
        if request.method == 'POST':
            resp = requests.post(remote_url, data=request.data, verify=True)
        else:
            resp = requests.get(remote_url, verify=True, timeout=30)
            
        print(f"--- RESOURCE PROXY: Response Status: {resp.status_code} ---")
        print(f"--- RESOURCE PROXY: Response Content-Type: {resp.headers.get('Content-Type')} ---")


        response_content = resp.content
        # WEBHOOK
        DEFAULT_WEBHOOK = b'https://devlinkv2.paydee.co/mpigw/mpi/payment-status/redirect'
        LOCAL_WEBHOOK = b'https://devlinkv2.paydee.co/mpigw/payment/status'

        # if DEFAULT_WEBHOOK in response_content:
        #     print(f"--- DEFAULT WEBHOOK PATCH APPLIED ---")
        #     response_content = response_content.replace(DEFAULT_WEBHOOK, LOCAL_WEBHOOK)

        # Return the content directly, ensuring correct MIME type is passed
        return response_content, resp.status_code, {'Content-Type': resp.headers['Content-Type']}
        
    except Exception as e:
        error = str(e)
        print(f"--- Resource Proxy Error: {error} ---")
        return f"Error proxying resource: {e}", 500
    
