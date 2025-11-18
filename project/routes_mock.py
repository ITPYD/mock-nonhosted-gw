import requests, os, random
from project import app
from datetime import date, time, datetime, timedelta
from flask import current_app, render_template, redirect, url_for, flash, request, send_file, send_from_directory, abort, Response
from werkzeug.utils import safe_join # This import should now be resolved

import project.routes
from project.mpi import MPI
from project.key import Key


#------------------------
# CORE PROXY FUNCTION
#------------------------
def _proxy_request(path, content_type, prefix=""):
    """Helper function to proxy requests (POST/GET) to the MPI_URL."""

    url = app.config["MPI_URL"] + path
    print(f"-----{prefix}: {path[1:]}---------")
    print(f"Proxying request to: {url}")
    
    # Determine which data source to use based on content type
    if 'json' in content_type:
        request_data = request.data
    else:
        # Use request.form for standard form submissions (x-www-form-urlencoded)
        request_data = request.form
        
    headers = {'Content-Type': content_type}
    
    # Determine the HTTP method to use for the request
    method = request.method.upper()

    try:
        # ... (omitting requests.post/get logic) ...
        if method == 'POST':
            r = requests.post(url, headers=headers, data=request_data, verify=False, timeout=30)
        else:
            r = requests.get(url, headers=headers, params=request_data, verify=False, timeout=30)
            
        response_content = r.content

         # --- TEMPORARY DEBUG PRINT START ---
        if path == "/maReq":
            print("--- DEBUG: FULL CONTENT FOR /maReq RESPONSE ---")
            # Decode the content to print the URL string clearly
            print(response_content.decode('utf-8', errors='ignore'))
            print("-----------------------------------------------")

        if path == "/mercReq":
            print("--- DEBUG: FULL CONTENT FOR /mercReq RESPONSE ---")
            # Decode the content to print the URL string clearly
            print(response_content.decode('utf-8', errors='ignore'))
            print("-----------------------------------------------")


        # === START: CROSS-ORIGIN FIX (3DS) ===
        # We only need to do this when the response is HTML and contains the specific 3DS domain.
        
        # 1. Define the remote 3DS URL prefix to be replaced (e.g., the iframe source)
        REMOTE_3DS_PREFIX = b'https://paydee-test.as1.gpayments.net'
        
        # 2. Define the local mock URL prefix
        # We use a path that maps to your new @app.route('/mock/3ds/<path:subpath>')
        LOCAL_3DS_PREFIX = b'/mock/3ds'
        
        if REMOTE_3DS_PREFIX in response_content:
            print("--- CROSS-ORIGIN PATCH APPLIED ---")
            response_content = response_content.replace(REMOTE_3DS_PREFIX, LOCAL_3DS_PREFIX)
        
        # === END: CROSS-ORIGIN FIX (3DS) ===

        # ===================================

        REMOTE_MPI_DOMAIN = app.config["REMOTE_MPI_DOMAIN"].encode('utf-8')
        LOCAL_ROOT_PATH = b'/'

        if REMOTE_MPI_DOMAIN in response_content:
            print(f"--- FINAL REDIRECT PATCH APPLIED (Replacing {REMOTE_MPI_DOMAIN.decode()} with {LOCAL_ROOT_PATH.decode()}) ---")
            # Replace the full remote MPI base URL with your local root path.
            # This makes the final form submit to your application's root path or relative link.
            response_content = response_content.replace(REMOTE_MPI_DOMAIN, LOCAL_ROOT_PATH)

        # ===================================

        # WEBHOOK
        DEFAULT_WEBHOOK = b'https://devlinkv2.paydee.co/mpigw/mpi/payment-status/redirect'
        LOCAL_WEBHOOK = b'https://devlinkv2.paydee.co/mpigw/payment/status'

        if DEFAULT_WEBHOOK in response_content:
            print(f"--- DEFAULT WEBHOOK PATCH APPLIED ---")
            response_content = response_content.replace(DEFAULT_WEBHOOK, LOCAL_WEBHOOK)



        print(f"--- Response: {r.status_code} ---")
        # print(response_content) # Print the modified content here for debugging
        
        # Return the modified content
        return Response(response_content, status=r.status_code)
        
    except Exception as e:
        # ... (error handling logic) ...
        error = str(e)
        print(f"--- Proxy Error --- \n{error}")
        return Response(error, status=500)

# def _proxy_request(path, content_type, prefix=""):
#     """Helper function to proxy requests (POST/GET) to the MPI_URL."""
#     url = app.config["MPI_URL"] + path
#     print(f"-----{prefix}: {path[1:]}---------")
#     print(f"Proxying request to: {url}")
    
#     # Determine which data source to use based on content type
#     if 'json' in content_type:
#         request_data = request.data
#     else:
#         # Use request.form for standard form submissions (x-www-form-urlencoded)
#         request_data = request.form
        
#     headers = {'Content-Type': content_type}
    
#     # Determine the HTTP method to use for the request
#     method = request.method.upper()

#     try:
#         if method == 'POST':
#             r = requests.post(url, headers=headers, data=request_data, verify=False, timeout=30)
#         else: # Default to GET for simplicity if not POST
#             r = requests.get(url, headers=headers, params=request_data, verify=False, timeout=30)

#         print(f"--- Response: {r.status_code} ---")
#         print(r.content)
#         return Response(r.content, status=r.status_code)
        
#     except Exception as e:
#         error = str(e)
#         print(f"--- Proxy Error --- \n{error}")
#         return Response(error, status=500)

#------------------------
# MOCK ROUTES (API ENDPOINTS)
#------------------------

# (Your existing imports: from flask import Flask, jsonify, request, Response)
# (Your existing imports: import requests, json)

# --- NEW HELPER FUNCTION FOR CUSTOM PAYLOADS ---
def _custom_proxy_request(path, data_payload, prefix=""):
    """
    Helper function to proxy requests (POST) with a SPECIFIC custom data payload.
    This bypasses using the global request.form, which is necessary for multi-step processing.
    """
    url = app.config["MPI_URL2"] + path
    print(f"-----{prefix}: {path[1:]} (CUSTOM PAYLOAD)---------")
    print(f"Proxying request to: {url}")
    
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    
    try:
        # Use requests.post directly with the custom data payload
        r = requests.post(url, headers=headers, data=data_payload, verify=False, timeout=30)
            
        response_content = r.content

        # === START: CONTENT PATCHING (CRITICAL) ===
        # The patching logic must be included here to handle redirects from the target server

        # 1. 3DS Domain Patching (if applicable)
        REMOTE_3DS_PREFIX = b'https://paydee-test.as1.gpayments.net'
        LOCAL_3DS_PREFIX = b'/mock/3ds'
        if REMOTE_3DS_PREFIX in response_content:
            response_content = response_content.replace(REMOTE_3DS_PREFIX, LOCAL_3DS_PREFIX)

        # 2. MPI Domain Patching
        REMOTE_MPI_DOMAIN = app.config["REMOTE_MPI_DOMAIN"].encode('utf-8')
        LOCAL_ROOT_PATH = b'/'
        if REMOTE_MPI_DOMAIN in response_content:
             response_content = response_content.replace(REMOTE_MPI_DOMAIN, LOCAL_ROOT_PATH)

        # 3. Webhook Patching (The final redirect URL)
        DEFAULT_WEBHOOK = b'https://devlinkv2.paydee.co/mpigw/mpi/payment-status/redirect'
        LOCAL_WEBHOOK = b'https://devlinkv2.paydee.co/mpigw/payment/status'
        if DEFAULT_WEBHOOK in response_content:
            response_content = response_content.replace(DEFAULT_WEBHOOK, LOCAL_WEBHOOK)
        # === END: CONTENT PATCHING ===
            
        print(f"--- Response: {r.status_code} ---")
        return Response(response_content, status=r.status_code)
            
    except Exception as e:
        error = str(e)
        print(f"--- Proxy Error --- \n{error}")
        return Response(error, status=500)


# --- UPDATED /mock/mpReq ROUTE ---
@app.route('/mock/mpReq', methods=['GET', 'POST'])
def mock_mpreq():
    """
    Handles the mock flow: 
    1. Proxies mercReq (transaction registration) using original data.
    2. Assumes success and constructs a new payload for fpx/init.
    3. Proxies the fpx/init request using the custom payload and returns the final response.
    """
    print(f" ==== mpReq === \n")
    
    # 1. Capture the original request data before it's used by the first proxy call.
    # This data contains critical fields like MPI_MERC_ID and MPI_EMAIL.
    original_data = dict(request.form)
    
    # 2. First call: Proxy the transaction registration (mercReq)
    # Note: We must call _proxy_request first to register the transaction and get a response.
    # For simplicity, we assume mercReq is successful (HTTP 200) and proceed.
    # The return value of the first call is ignored because we want to return the FPX initiation page.
    ret = _proxy_request("/mercReq", 'application/x-www-form-urlencoded', prefix="mock")


    # 3. Construct the data payload for fpx/init
    # This payload is for the second request, which initiates the bank selection screen.
    fpx_data_payload = {
        # Copied/Derived from the incoming request (mercReq)
        "PAG_MERCHANT_ID": original_data.get('MPI_MERC_ID', '000000000000033'),
        "PAG_CUST_EMAIL": original_data.get('MPI_EMAIL', 'test@example.com'),
        
        # New/Hardcoded/Selected data for FPX initiation
        # Note: PAG_TRANS_ID should ideally be derived or newly generated to be unique.
        "PAG_TRANS_ID": original_data.get('MPI_TRXN_ID', 'mdl_default_id'),
        "PAG_CHANNEL_NAME": "Bank Muamalat", # Example bank selection
        "PAG_ORDER_DETAIL": "PAG Merchant Order",
        "PAG_MAC": "Some-Random-MAC-String-For-FPX", # Placeholder MAC for FPX
    }
    
    # 4. Second call: FPX initiation (/fpx/init) using the custom payload
    # This returns the final HTML to the client (usually the bank selection/redirect page).
    return _custom_proxy_request("mpigw/fpx/init", fpx_data_payload, prefix="mock")

# 
@app.route('/mock/mercReq', methods=['GET', 'POST'])
def mock_mercreq():
    return _proxy_request("/mercReq", 'application/x-www-form-urlencoded', prefix="mock")

# The route that returns the HTML form
@app.route('/mock/mkReq', methods=['GET', 'POST'])
def mock_mkreq():
    print("debug")
    # Note: Ensure the path casing here matches the remote API
    return _proxy_request("/mkReq", 'application/json', prefix="mock")

# NEW: Route to handle the form submission action "cardReq"
@app.route('/mock/cardReq', methods=['POST'])
def mock_card_req():
    """Handles the form submission from the proxied HTML page."""
    # This route intercepts the POST from the HTML form and proxies it to the remote API
    return _proxy_request("/cardReq", 'application/x-www-form-urlencoded', prefix="mock")

@app.route('/mock/maReq', methods=['POST'])
def mock_mareq():
    """Handles the form submission action 'maReq' and proxies it to the remote MPI."""
    # This request contains the final browser info and is a standard form submission.
    return _proxy_request("/maReq", 'application/x-www-form-urlencoded', prefix="mock")

@app.route('/mock/notifyReq', methods=['POST'])
def mock_notify_req():
    """Handles the final form submission from the 3DS iFrame and proxies it."""
    # This request should be proxied back to the remote MPI server to complete the 3DS flow.
    return _proxy_request("/notifyReq", 'application/x-www-form-urlencoded', prefix="mock")

from flask import Flask, jsonify, request, Response
import json # You'll need this import if not already present

# Assume 'app = Flask(__name__)' is already defined

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
        

        # NEW: The final MPI domain to be patched
        REMOTE_MPI_DOMAIN = b'https://devlink.paydee.co/mpi/notifyReq'
        LOCAL_NOTIFY_PATH = b'/mock/notifyReq' # Create this new route


        if REMOTE_3DS_PREFIX in response_content:
            print(f"--- 3DS PROXY PATCH APPLIED: {subpath} ---")
            response_content = response_content.replace(REMOTE_3DS_PREFIX, LOCAL_3DS_PREFIX)
        
        # CRITICAL NEW PATCHING STEP: Handle the final form action URL
        if REMOTE_MPI_DOMAIN in response_content:
            print(f"--- 3DS PROXY PATCH APPLIED (MPI domain): {subpath} ---")
            response_content = response_content.replace(REMOTE_MPI_DOMAIN, LOCAL_NOTIFY_PATH)


        # WEBHOOK
        DEFAULT_WEBHOOK = b'https://devlinkv2.paydee.co/mpigw/mpi/payment-status/redirect'
        LOCAL_WEBHOOK = b'https://devlinkv2.paydee.co/mpigw/payment/status'

        if DEFAULT_WEBHOOK in response_content:
            print(f"--- DEFAULT WEBHOOK PATCH APPLIED ---")
            response_content = response_content.replace(DEFAULT_WEBHOOK, LOCAL_WEBHOOK)

        # 3. Return the patched content with all original response headers
        return Response(response_content, status=resp.status_code, headers=resp.headers)
        
    except Exception as e:
        error = str(e)
        print(f"--- 3DS Proxy Error: {error} ---")
        return f"Error proxying 3DS: {e}", 500


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

        if DEFAULT_WEBHOOK in response_content:
            print(f"--- DEFAULT WEBHOOK PATCH APPLIED ---")
            response_content = response_content.replace(DEFAULT_WEBHOOK, LOCAL_WEBHOOK)

        # Return the content directly, ensuring correct MIME type is passed
        return response_content, resp.status_code, {'Content-Type': resp.headers['Content-Type']}
        
    except Exception as e:
        error = str(e)
        print(f"--- Resource Proxy Error: {error} ---")
        return f"Error proxying resource: {e}", 500
    
