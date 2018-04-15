from flask import request, session
from flask_api import status

import testteamreports.data.operations as ops
from testteamreports.service import app
from testteamreports.service import api_keys


def check_password(login: str, password: str):
    user_record = ops.get_user_by_login(login)
    pwd_hash = ops.encode_pwd(password)
    return user_record is not None \
           and user_record.pwd_hash == pwd_hash


@app.route('/login', methods=['GET', 'POST'])
def do_login():
    if request.method == 'GET':
        return 'Please log in with POST method', status.HTTP_405_METHOD_NOT_ALLOWED
    elif request.method == 'POST':
        login = request.json[api_keys.LOGIN]
        if check_password(login, request.json[api_keys.PASSWORD]):
            session[api_keys.LOGGED_IN] = True
            session[api_keys.LOGIN] = login
            return 'Login OK', status.HTTP_200_OK
        else:
            return '', status.HTTP_401_UNAUTHORIZED


@app.route('/logout', methods=['GET', 'POST'])
def do_logout():
    if request.method == 'GET':
        return 'Please log out with POST method', status.HTTP_405_METHOD_NOT_ALLOWED
    elif request.method == 'POST':
        session[api_keys.LOGGED_IN] = False
        return 'Logged out', status.HTTP_200_OK
