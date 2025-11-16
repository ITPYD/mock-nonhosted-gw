import requests, os, random
from project import app
from datetime import date, time, datetime, timedelta
from flask import current_app, render_template, redirect, url_for, flash, request, send_file, send_from_directory, abort, Response
from werkzeug.utils import safe_join

import project.routes
from project.mpi import MPI
from project.key import Key



# ---------------------
# MPI Function
# ---------------------    



#------------------------
# Proxy functions
#------------------------

def _proxy_request(path, content_type, prefix=""):
    """Helper function to proxy requests to the MPI_URL."""
    url = app.config["MPI_URL"] + path
    print(f"-----{prefix}: {path[1:]}---------")
    print(f"Proxying request to: {url}")
    
    request_data = request.data if 'json' in content_type else request.form
    headers = {'Content-Type': content_type}

    try:
        # Note: verify=False is a security risk. Use verify=True in production.
        r = requests.post(url, headers=headers, data=request_data, verify=False)
        print(f"--- Response: {r.status_code} ---")
        print(r.content)
        return Response(r.content, status=r.status_code)
    except Exception as e:
        error = str(e)
        print(f"--- Proxy Error --- \n{error}")
        return Response(error, status=500)

@app.route('/mock/mpReq', methods=['GET', 'POST'])
def mock_mpreq():
    return _proxy_request("/mpReq", 'application/x-www-form-urlencoded', prefix="mock")

@app.route('/mock/mercReq', methods=['GET', 'POST'])
def mock_mercreq():
    return _proxy_request("/mercReq", 'application/x-www-form-urlencoded', prefix="mock")

@app.route('/mock/mkReq', methods=['GET', 'POST'])
def mock_mkreq():
    return _proxy_request("/mkReq", 'application/json', prefix="mock")
