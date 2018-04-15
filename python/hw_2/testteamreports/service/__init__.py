from flask import Flask, session
from flask_api import status
from functools import wraps

import testteamreports.data.operations as ops
from testteamreports.settings import ADMIN_LOGIN
from testteamreports.service import api_keys

app = Flask(__name__)
app.secret_key = '54b165c37f02f21bb8cefc66d0a0b801515d0013f0dab7843ca7aac7da9f8b2c'


@app.before_request
def _db_connect():
    ops.db.connect()


@app.teardown_request
def _db_close(exc):
    if not ops.db.is_closed():
        ops.db.close()


def user_login_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not session.get(api_keys.LOGGED_IN) \
                or session.get(api_keys.LOGIN) == ADMIN_LOGIN:
            return '', status.HTTP_401_UNAUTHORIZED
        return func(*args, **kwargs)

    return decorated_view


def admin_login_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not session.get(api_keys.LOGGED_IN) \
                or session.get(api_keys.LOGIN) != ADMIN_LOGIN:
            return '', status.HTTP_401_UNAUTHORIZED
        return func(*args, **kwargs)

    return decorated_view


###########################################################
# IMPORT ALL CONTROLLERS
import testteamreports.service.admin_controllers
import testteamreports.service.login_controllers
import testteamreports.service.data_controllers
