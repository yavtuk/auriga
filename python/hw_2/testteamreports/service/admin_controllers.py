from flask import request, jsonify
from flask_api import status

import testteamreports.data.operations as ops
from testteamreports.service import app, admin_login_required
from testteamreports.service import api_keys


@app.route('/admin/users', methods=['GET'])
@admin_login_required
def get_users():
    return jsonify(ops.get_all_logins())


@app.route('/admin/user', methods=['POST'])
@admin_login_required
def add_user():
    user_id = ops.add_user_record(
        request.json[api_keys.NEW_LOGIN],
        request.json[api_keys.NEW_PASSWORD]
    )
    return jsonify({api_keys.ID: user_id}), status.HTTP_201_CREATED


@app.route('/admin/recreatedb', methods=['POST'])
@admin_login_required
def recreate_db():
    new_admin_password = request.form.get(api_keys.NEW_PASSWORD, None)
    ops.recreate_db(new_admin_password)
    return 'OK.', status.HTTP_200_OK
