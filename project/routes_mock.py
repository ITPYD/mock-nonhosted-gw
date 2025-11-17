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
        if method == 'POST':
            r = requests.post(url, headers=headers, data=request_data, verify=False, timeout=30)
        else: # Default to GET for simplicity if not POST
            r = requests.get(url, headers=headers, params=request_data, verify=False, timeout=30)

        print(f"--- Response: {r.status_code} ---")
        print(r.content)
        return Response(r.content, status=r.status_code)
        
    except Exception as e:
        error = str(e)
        print(f"--- Proxy Error --- \n{error}")
        return Response(error, status=500)

#------------------------
# MOCK ROUTES (API ENDPOINTS)
#------------------------

@app.route('/mock/mpReq', methods=['GET', 'POST'])
def mock_mpreq():
    return _proxy_request("/mpReq", 'application/x-www-form-urlencoded', prefix="mock")

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


#------------------------
# STATIC RESOURCE PROXY (CRITICAL FIX FOR CSS/JS/IMAGES)
#------------------------

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

        # Return the content directly, ensuring correct MIME type is passed
        return resp.content, resp.status_code, {'Content-Type': resp.headers['Content-Type']}
        
    except Exception as e:
        error = str(e)
        print(f"--- Resource Proxy Error: {error} ---")
        return f"Error proxying resource: {e}", 500
    
