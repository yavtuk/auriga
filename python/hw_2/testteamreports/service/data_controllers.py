from flask import request, jsonify, send_from_directory
from flask_api import status
import os

import testteamreports.data.operations as ops
from testteamreports.reports import testrun_pdf
from testteamreports.service import app, user_login_required
from testteamreports.service import api_keys
from testteamreports.util import convert

from testteamreports.settings import REPORT_STORAGE_FOLDER


@app.route('/reqs', methods=['GET'])
@user_login_required
def get_all_requirements():
    return jsonify([{
        api_keys.ID: x.get_id(),
        api_keys.NAME: x.name,
        api_keys.RISK: x.risk
    } for x in ops.get_all_requirements()])


@app.route('/req', methods=['POST'])
@user_login_required
def new_requirement():
    new_id = ops.add_requirement(
        name=request.json[api_keys.NAME],
        risk=request.json[api_keys.RISK]
    )
    return jsonify({api_keys.ID: new_id}), status.HTTP_201_CREATED


@app.route('/testcases', methods=['GET'])
@user_login_required
def get_all_test_cases():
    return jsonify([{
        api_keys.ID: x.get_id(),
        api_keys.NAME: x.name,
        api_keys.REQUIREMENTS: [req.name for req in ops.get_all_requirements_for_test(x)]
    } for x in ops.get_all_test_cases()])


@app.route('/testcase', methods=['POST'])
@user_login_required
def new_test_case():
    testcase_name = request.json[api_keys.NAME]
    new_case_id = ops.add_test_case(testcase_name)

    if api_keys.REQUIREMENTS in request.json:
        ops.link_case_to_requirements(testcase_name, list(request.json[api_keys.REQUIREMENTS]))

    return jsonify({api_keys.ID: new_case_id}), status.HTTP_201_CREATED


@app.route('/testruns', methods=['GET'])
@user_login_required
def get_all_test_runs():
    return jsonify([{
        api_keys.ID: x.get_id(),
        api_keys.START_DATE: convert.to_isoz_date_string(x.start_date),
        api_keys.END_DATE: convert.to_isoz_date_string(x.end_date),
        api_keys.DESCRIPTION: x.description,
        api_keys.TEST_CASES: [case.name for case in ops.get_all_tests_in_set(x)]
    } for x in ops.get_all_test_runs()])


@app.route('/testrun', methods=['POST'])
@user_login_required
def new_test_run():
    new_run_id = ops.add_test_run(
        start_date=convert.from_isoz_date_string(request.json[api_keys.START_DATE]),
        end_date=convert.from_isoz_date_string(request.json[api_keys.END_DATE]),
        description=request.json[api_keys.DESCRIPTION]
    )

    if api_keys.TEST_CASES in request.json:
        ops.add_test_set(new_run_id, list(request.json[api_keys.TEST_CASES]))

    return jsonify({api_keys.ID: new_run_id}), status.HTTP_201_CREATED


@app.route('/testrun/<int:testrun_id>/results', methods=['GET'])
@user_login_required
def get_testrun_report(testrun_id):
    return jsonify([
        {
            api_keys.NAME: x.test_case.name,
            api_keys.IS_PASSED: x.is_passed,
            api_keys.DATE_TIME: convert.to_isoz_datetime_string(x.date_time)
        } for x in ops.get_all_test_results(testrun_id)
    ])


@app.route('/testrun/<int:testrun_id>/result', methods=['POST'])
@user_login_required
def add_test_result(testrun_id):
    ops.add_test_result(
        testrun_id=testrun_id,
        testcase_name=request.json[api_keys.NAME],
        is_passed=request.json[api_keys.IS_PASSED],
        date_time=convert.from_isoz_datetime_string(request.json[api_keys.DATE_TIME])
    )
    return '', status.HTTP_201_CREATED


@app.route('/testrun/<int:testrun_id>/pdf', methods=['GET'])
@user_login_required
def get_testrun_report_pdf(testrun_id):
    file_name = testrun_pdf.create_testrun_summary_pdf(testrun_id)
    return send_from_directory(os.path.join(os.getcwd(), REPORT_STORAGE_FOLDER), file_name)
