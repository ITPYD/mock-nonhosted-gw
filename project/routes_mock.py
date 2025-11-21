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
    url = app.config["MPIGW_URL"] + path
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
        # if path == "/maReq":
        #     print("--- DEBUG: FULL CONTENT FOR /maReq RESPONSE ---")
        #     # Decode the content to print the URL string clearly
        #     print(response_content.decode('utf-8', errors='ignore'))
        #     print("-----------------------------------------------")

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
        
        # if REMOTE_3DS_PREFIX in response_content:
        #     print("--- CROSS-ORIGIN PATCH APPLIED ---")
        #     response_content = response_content.replace(REMOTE_3DS_PREFIX, LOCAL_3DS_PREFIX)
        
        # === END: CROSS-ORIGIN FIX (3DS) ===

        # ===================================
        # app.config['REMOTE_MPI_DOMAIN'] = "https://devlink.paydee.co/mpi"
        REMOTE_MPI_DOMAIN = app.config["REMOTE_MPI_DOMAIN"].encode('utf-8')
        LOCAL_ROOT_PATH = b'/'

        # if REMOTE_MPI_DOMAIN in response_content:
        #     print(f"--- FINAL REDIRECT PATCH APPLIED (Replacing {REMOTE_MPI_DOMAIN.decode()} with {LOCAL_ROOT_PATH.decode()}) ---")
        #     # Replace the full remote MPI base URL with your local root path.
        #     # This makes the final form submit to your application's root path or relative link.
        #     response_content = response_content.replace(REMOTE_MPI_DOMAIN, LOCAL_ROOT_PATH)

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


#------------------------
# MOCK ROUTES (API ENDPOINTS)
#------------------------

# def _custom_proxy_request(path, data_payload, prefix=""):
#     """
#     HITS the REMOTE MPI SERVER for /fpx/init or /wallet/init.
#     CRITICAL: It applies content patches and strips frame-busting headers 
#     to ensure the response HTML works inside an iframe.
#     The final Response object containing the patched HTML is returned.
#     """
#     # Using app.config["MPI_URL2"] as per your provided code
#     url = app.config["MPI_URL2"] + path
#     print(f"-----{prefix}: {path[1:]} (CUSTOM PAYLOAD)---------")
#     print(f"Proxying request to: {url}")
#     print(f"Custom data payload: {data_payload}")
    
#     headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    
#     # --- CRITICAL: REAL API CALL IS NOW ACTIVE ---
#     try:
#         # --- START REAL API CALL ---
#         print("--- EXECUTING REAL requests.post TO EXTERNAL GATEWAY ---")
#         r = requests.post(url, headers=headers, data=data_payload, verify=False, timeout=30)
#         response_content = r.content
#         r_status_code = r.status_code
#         # --- END REAL API CALL ---

#         # === START: HEADER STRIPPING AND CONTENT PATCHING (CRITICAL FIXES) ===

#         # 0. HEADER STRIPPING (To prevent external frame-breaking)
#         response_headers = dict(r.headers)
        
#         # Headers to strip because they prevent iframe loading
#         headers_to_strip = [
#             'X-Frame-Options', 
#             'Strict-Transport-Security'
#         ]
        
#         for header in headers_to_strip:
#             if header.lower() in [k.lower() for k in response_headers.keys()]:
#                 # Find the actual case-sensitive key and remove it
#                 key_to_remove = next(k for k in response_headers.keys() if k.lower() == header.lower())
#                 print(f"--- STRIPPING HEADER: {key_to_remove} ---")
#                 response_headers.pop(key_to_remove, None)
                
#         # Handle specific CSP directives if Content-Security-Policy exists
#         csp_key = next((k for k in response_headers.keys() if k.lower() == 'content-security-policy'), None)

#         if csp_key:
#             csp = response_headers[csp_key]
#             if 'frame-ancestors' in csp:
#                 # Attempt to remove frame-ancestors directive
#                 csp_parts = [p for p in csp.split(';') if 'frame-ancestors' not in p.strip()]
#                 new_csp = '; '.join(csp_parts).strip()
#                 response_headers[csp_key] = new_csp
#                 print("--- CSP PATCH: Removed frame-ancestors directive ---")

        
#         print("--- DEBUG: FULL CONTENT FOR /fpx/init RESPONSE (Before Patch) ---")
#         print(response_content.decode('utf-8', errors='ignore'))
#         print("-------------------------------------------------------------------")

#         # Define domains to be replaced
#         REMOTE_DOMAIN_V3 = b'https://devlinkv3.paydee.co'
#         LOCAL_HOST_PREFIX = b'/' 
        
#         # Patch 6: CRITICAL FPX Submit Action Reroute (to handle the final CSP break)
#         FPX_EXTERNAL_ACTION = b'https://uat.mepsfpx.com.my/FPXMain/seller2DReceiver.jsp'
#         FPX_LOCAL_ACTION = b'/mpigw/fpx/mepsfpx_submit'
#         if FPX_EXTERNAL_ACTION in response_content:
#             print(f"--- PATCH: Rewriting FPX Form action from {FPX_EXTERNAL_ACTION.decode()} to {FPX_LOCAL_ACTION.decode()} ---")
#             response_content = response_content.replace(FPX_EXTERNAL_ACTION, FPX_LOCAL_ACTION)

#         # 4. CRITICAL: Fix for Cross-Origin Navigation
#         force_top = data_payload.get('FORCE_TARGET_TOP') == '1'
        
#         # Patch 1: Change form target="_top" to target="_self" (Conditional)
#         if b'target="_top"' in response_content:
#             if not force_top:
#                 print("--- PATCH: Changing target=\"_top\" to target=\"_self\" ---")
#                 response_content = response_content.replace(b'target="_top"', b'target="_self"')
#             else:
#                 print("--- OVERRIDE: FORCE_TARGET_TOP=1 is set. Retaining target=\"_top\" in external response. ---")


#         # Patch 2: Change JavaScript window.top/parent.location redirects to window.self.location
#         if b'window.top.location' in response_content or b'window.parent.location' in response_content:
#             print("--- PATCH: Changing window.top/parent.location to window.self.location ---")
#             response_content = response_content.replace(b'window.top.location', b'window.self.location')
#             response_content = response_content.replace(b'window.parent.location', b'window.self.location')
            
#         # 5. CRITICAL: REROUTE ALL EXTERNAL HOST REFERENCES to LOCAL HOST (The most robust fix)
#         # This fixes the 404 (by rerouting /redirect) AND fixes broken asset links (CSS/JS/images).
#         if REMOTE_DOMAIN_V3 in response_content:
#             print(f"--- PATCH: Rewriting ALL {REMOTE_DOMAIN_V3.decode()} to {LOCAL_HOST_PREFIX.decode()} ---")
#             # This handles /redirect, /resources, /img, etc.
#             response_content = response_content.replace(REMOTE_DOMAIN_V3, LOCAL_HOST_PREFIX)

#         # The rest of your domain patching (retained for specific cases):
        
#         # 1. 3DS Domain Patching (if applicable)
#         REMOTE_3DS_PREFIX = b'https://paydee-test.as1.gpayments.net'
#         LOCAL_3DS_PREFIX = b'/mock/3ds'
#         if REMOTE_3DS_PREFIX in response_content:
#             print("--- PATCH: 3DS Domain Fix Applied ---")
#             response_content = response_content.replace(REMOTE_3DS_PREFIX, LOCAL_3DS_PREFIX)

#         # 2. MPI Domain Patching
#         REMOTE_MPI_DOMAIN = app.config["REMOTE_MPI_DOMAIN"].encode('utf-8')
#         LOCAL_ROOT_PATH = b'/'
#         if REMOTE_MPI_DOMAIN in response_content and REMOTE_MPI_DOMAIN != REMOTE_DOMAIN_V3:
#             print("--- PATCH: Secondary MPI Domain Fix Applied ---")
#             response_content = response_content.replace(REMOTE_MPI_DOMAIN, LOCAL_ROOT_PATH)

#         # 3. Webhook Patching (The final redirect URL) - May be covered by Patch 5, but kept for specificity
#         DEFAULT_WEBHOOK = b'https://devlinkv2.paydee.co/mpigw/mpi/payment-status/redirect'
#         LOCAL_WEBHOOK = b'https://devlinkv2.paydee.co/mpigw/payment/status'
#         if DEFAULT_WEBHOOK in response_content:
#             print("--- PATCH: Default Webhook Fix Applied ---")
#             response_content = response_content.replace(DEFAULT_WEBHOOK, LOCAL_WEBHOOK)
            
#         # Patch 7: CRITICAL: Force immediate submission if a form exists (to bypass confirmation modals/popups)
#         if b'<form' in response_content:
#             print("--- PATCH: Injecting force submit script to bypass potential confirmation popups ---")
            
#             # We will inject a script to execute the form submit slightly delayed, 
#             # ensuring it runs after the original onload/onclick handlers are set up.
#             force_submit_script = b'<script>setTimeout(function(){ if(document.forms.length > 0) { document.forms[0].submit(); console.log("Form auto-submitted by proxy patch."); } }, 50);</script>'
            
#             # Use lower() on response_content for case-insensitive replacement
#             # Replace only the first instance to ensure we place it right before the end of the body
#             content_lower = response_content.lower()
#             if b'</body>' in content_lower:
#                 # Find the position of </body> in the original content (case-sensitive)
#                 # To avoid issues with mixed case content, we use the original content for replacement
#                 body_end_index = content_lower.rfind(b'</body>')
#                 if body_end_index != -1:
#                     response_content = (
#                         response_content[:body_end_index] + 
#                         force_submit_script + 
#                         response_content[body_end_index:]
#                     )
#             else:
#                 # Fallback: append to the end
#                 response_content += force_submit_script


#         # === END: CONTENT PATCHING ===
            
#         print(f"--- Response: {r_status_code} ---")
#         return Response(response_content, 
#                         status=r_status_code, 
#                         headers=response_headers, # Include custom headers
#                         mimetype=r.headers.get('content-type', 'text/html')) # <--- Updated return
            
#     except Exception as e:
#         error = str(e)
#         print(f"--- Proxy Error --- \n{error}")
#         return Response(error, status=500)

# --- NEW HELPER FUNCTION FOR CUSTOM PAYLOADS ---
def _custom_proxy_request(path, data_payload, prefix=""):
    """
    Helper function to proxy requests (POST) with a SPECIFIC custom data payload.
    This bypasses using the global request.form, which is necessary for multi-step processing.
    """
    url = app.config["MPI_URL2"] + path
    print(f"-----{prefix}: {path[1:]} (CUSTOM PAYLOAD)---------")
    print(f"Proxying request to: {url}")
    print(f"Custom data payload: {data_payload}")
    
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    
    try:
        # Use requests.post directly with the custom data payload
        r = requests.post(url, headers=headers, data=data_payload, verify=False, timeout=30)
            
        response_content = r.content


        print("--- DEBUG: FULL CONTENT FOR /mpigw/fpx/init RESPONSE ---")
        # Decode the content to print the URL string clearly
        print(response_content.decode('utf-8', errors='ignore'))
        print("-----------------------------------------------")

        # === START: CONTENT PATCHING (CRITICAL) ===
        # The patching logic must be included here to handle redirects from the target server

        # 1. 3DS Domain Patching (if applicable)
        REMOTE_3DS_PREFIX = b'https://paydee-test.as1.gpayments.net'
        LOCAL_3DS_PREFIX = b'/mock/3ds'
        # if REMOTE_3DS_PREFIX in response_content:
        #     response_content = response_content.replace(REMOTE_3DS_PREFIX, LOCAL_3DS_PREFIX)

        # 2. MPI Domain Patching
        REMOTE_MPI_DOMAIN = app.config["REMOTE_MPI_DOMAIN"].encode('utf-8')
        LOCAL_ROOT_PATH = b'/'
        # if REMOTE_MPI_DOMAIN in response_content:
        #      response_content = response_content.replace(REMOTE_MPI_DOMAIN, LOCAL_ROOT_PATH)

        # 3. Webhook Patching (The final redirect URL)
        DEFAULT_WEBHOOK = b'https://devlinkv2.paydee.co/mpigw/mpi/payment-status/redirect'
        LOCAL_WEBHOOK = b'https://devlinkv2.paydee.co/mpigw/payment/status'
        # if DEFAULT_WEBHOOK in response_content:
        #     response_content = response_content.replace(DEFAULT_WEBHOOK, LOCAL_WEBHOOK)
        # === END: CONTENT PATCHING ===
            
        # 4. Replace target=top
        # OLD_TARGET = b'target="_top"'
        # NEW_TARGET = b''
        # if OLD_TARGET in response_content:
        #     response_content = response_content.replace(OLD_TARGET, NEW_TARGET)


        print(f"--- Response: {r.status_code} ---")
        return Response(response_content, status=r.status_code)
            
    except Exception as e:
        error = str(e)
        print(f"--- Proxy Error --- \n{error}")
        return Response(error, status=500)


# --- UPDATED /mock/mpReq ROUTE ---
@app.route('/pag/mpReq', methods=['GET', 'POST'])
@app.route('/mock/mpReq', methods=['GET', 'POST'])
def mock_mpreq():
    """
    Handles the mock flow (mercReq -> return manual click-through form posting 
    directly to external /fpx/init with target="_top").
    """
    # 3. Define the external endpoint and generate the manual click form
    EXTERNAL_INIT_URL = app.config["EXTERNAL_INIT_URL"]

    original_data = dict(request.form)
    # Get the channel ID from original data, retaining its casing.
    channel_id = original_data.get('MPI_PAYMENT_CHANNEL_ID', 'Public Bank')
    
    # Use the uppercase version for internal comparison logic (Fpx vs Wallet)
    channel_id_upper = channel_id.upper()
    
    if channel_id_upper in ('BOOST', 'GRABPAY', 'TNG-EWALLET', 'MB2U_QRPAY-PUSH', 'SHOPEEPAY', 'ALIPAY', 'GUPOP'):
        default_channel_name = channel_id 
        ext_url = "{EXTERNAL_INIT_URL}/wallet/init"
    else:
        default_channel_name = channel_id
        ext_url = "{EXTERNAL_INIT_URL}/fpx/init"

    # 1. Proxies mercReq
    ret = _proxy_request("/mercReq", 'application/x-www-form-urlencoded', prefix="mock")

    # Check the result of the mercReq proxy call using the Response object's .status_code
    if ret.status_code != 200: 
        error_message = ret.get_data(as_text=True) 
        return Response(f"Transaction Registration Failed: {error_message}", status=ret.status_code)

    # 2. Construct initiation payload (Merge original data and new PAG fields)
    
    # Start the payload with ALL original form data
    redirect_payload = dict(original_data)
    
    # Overwrite/Add the specific fields required for the next proxy hop (/fpx/init)
    # This ensures that even if 'MPI_MERC_ID' was missing, 'PAG_MERCHANT_ID' is still set.
    redirect_payload.update({
        "PAG_MERCHANT_ID": original_data.get('MPI_MERC_ID', '000000000000033'),
        "PAG_CUST_EMAIL": original_data.get('MPI_EMAIL', 'test@example.com'),
        "PAG_TRANS_ID": original_data.get('MPI_TRXN_ID', 'mdl_default_id'),
        "PAG_CHANNEL_NAME": default_channel_name,
        "PAG_ORDER_DETAIL": "PAG Merchant Order",
        "PAG_MAC": "Some-Random-MAC-String-For-FPX", 
        # Any other hardcoded fields for the /fpx/submit stage should go here
    })
    
    # Create hidden inputs from the payload
    hidden_inputs = ''.join(
        f'<input type="hidden" name="{k}" value="{v}">' 
        for k, v in redirect_payload.items()
    )


    
    # Generate the manual click HTML form to POST the fpx_data_payload to the external endpoint
    form_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Processing Payment...</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{ font-family: sans-serif; text-align: center; padding-top: 50px; background-color: #f7f7f7; }}
            .card {{ background-color: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); max-width: 400px; margin: 0 auto; }}
            h2 {{ color: #333; margin-bottom: 20px; }}
            p {{ color: #555; margin-bottom: 25px; }}
            button {{ 
                padding: 12px 25px; 
                font-size: 16px; 
                cursor: pointer; 
                background-color: #3498db; 
                color: white; 
                border: none; 
                border-radius: 8px;
                transition: background-color 0.3s;
            }}
            button:hover {{ background-color: #2980b9; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h2>Payment Redirection Required</h2>
            <p>Your browser requires a manual step to securely load the external payment gateway in the main window.</p>
            <form method="post" action="{ext_url}" target="_top">
                {hidden_inputs}
                <button type="submit">Continue to Payment Gateway</button>
            </form>
            <p style="margin-top: 25px; font-size: 0.8em; color: #777;">(This action will navigate away from the current page.)</p>
        </div>
    </body>
    </html>
    """
    
    print(f"--- DEBUG: Returning Manual Click Form posting directly to {ext_url} with target=_top ---")
    return Response(form_html, mimetype='text/html')

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
    
