import requests, os, random
from project import app, czws, db, bcrypt
from datetime import date, time, datetime, timedelta
from flask import current_app, render_template, redirect, url_for, flash, request, send_file, send_from_directory, safe_join, abort, Response

import project.routes
from project.mpi import MPI
from project.key import Key



# ---------------------
# MPI Function
# ---------------------    



#------------------------
# Proxy functions
#------------------------

@app.route('/mock/mkReq', methods=['GET', 'POST'])
def mock_mkreq():

    print("-----mock: mkreq---------")

#    result="OK"
#    return Response(result, status=200)

    url = app.config["MPI_URL"] + "/mkReq"
    print(url)
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

@app.route('/mock/mpReq', methods=['GET', 'POST'])
def mock_mpreq():
    url = app.config["MPI_URL"] + "/mpReq"
    #url="http://localhost:5000/mpi_status"
    print(url)

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

@app.route('/mock/mercReq', methods=['GET', 'POST'])
def mock_mercreq():
    url = app.config["MPI_URL"] + "/mercReq"
    #url="http://localhost:5000/mpi_status"
    print(url)    
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
