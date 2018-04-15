import hashlib
import traceback

from datetime import date, datetime
from sys import stderr
from typing import List

from testteamreports.data.model import db
from testteamreports.data.model import all_tables
from testteamreports.data.model import UserRecord
from testteamreports.data.model import Requirement, RequirementToTestCase
from testteamreports.data.model import TestCase, TestRun, TestCaseSet
from testteamreports.data.model import TestResult

from testteamreports.settings import ADMIN_LOGIN, ADMIN_FACTORY_PASSWORD


def encode_pwd(pwd: str) -> str:
    return hashlib.sha256(pwd.encode()).hexdigest()


#######################################
# DATABASE MANAGEMENT
#######################################

@db.atomic('EXCLUSIVE')
def recreate_db(admin_password=None) -> None:
    new_password = ADMIN_FACTORY_PASSWORD if admin_password is None else admin_password
    db.drop_tables(all_tables)
    db.create_tables(all_tables)
    UserRecord(login=ADMIN_LOGIN,
               pwd_hash=encode_pwd(new_password)).save()


#######################################
# USER MANAGEMENT
#######################################

@db.atomic('EXCLUSIVE')
def add_user_record(login: str, password: str) -> int:
    user = UserRecord(login=login, pwd_hash=encode_pwd(password))
    user.save()
    return user.get_id()


@db.atomic('EXCLUSIVE')
def get_user_by_login(login: str) -> [UserRecord, None]:
    try:
        return UserRecord.get(UserRecord.login == login)
    except:
        traceback.print_exc()
        return None


@db.atomic('EXCLUSIVE')
def get_all_logins() -> List[UserRecord]:
    return [x.login for x in UserRecord.select(UserRecord.login)]


#######################################
# CREATING DATA ITEMS
#######################################

@db.atomic('EXCLUSIVE')
def get_all_requirements() -> List[Requirement]:
    return list(Requirement.select())


@db.atomic('EXCLUSIVE')
def add_requirement(name: str, risk: int) -> int:
    req = Requirement(name=name, risk=risk)
    req.save()
    return req.get_id()


@db.atomic('EXCLUSIVE')
def get_all_test_runs() -> List[TestRun]:
    return list(TestRun.select())


@db.atomic('EXCLUSIVE')
def get_test_run_by_id(testrun_id: int) -> TestRun:
    return TestRun.get_by_id(testrun_id)


@db.atomic('EXCLUSIVE')
def add_test_run(start_date: date, end_date: date, description: str) -> int:
    tr = TestRun(start_date=start_date,
                 end_date=end_date,
                 description=description)
    tr.save()
    return tr.get_id()


@db.atomic('EXCLUSIVE')
def get_all_test_cases() -> List[TestCase]:
    return list(TestCase.select())


@db.atomic('EXCLUSIVE')
def add_test_case(name: str) -> int:
    tc = TestCase(name=name)
    tc.save()
    return tc.get_id()


#######################################
# LINKING DATA ITEMS
#######################################

@db.atomic('EXCLUSIVE')
def link_case_to_requirements(testcase_name: str, req_names: List[str]) -> None:
    test_case = TestCase.get(name=testcase_name)
    reqs = list(Requirement.select().where(Requirement.name.in_(req_names)))

    # Verify that all items have been found (assuming Requirement.name is unique)
    if len(reqs) < len(req_names):
        print("Found requirements: " + repr([x.name for x in reqs]), file=stderr)
        raise LookupError("Not all requirements have been found")

    # Create records
    req_ids = [req.get_id() for req in reqs]
    for req_id in req_ids:
        next_req = Requirement.get_by_id(req_id)
        RequirementToTestCase(requirement=next_req, test_case=test_case).save()


@db.atomic('EXCLUSIVE')
def add_test_set(testrun_id: int, testcase_names: List[str]) -> None:
    test_run = TestRun.get_by_id(testrun_id)
    test_cases = list(TestCase.select().where(TestCase.name.in_(testcase_names)))

    # Verify that all cases have been found (assuming TestCase.name is unique)
    if len(test_cases) < len(testcase_names):
        print("Found test cases: " + repr([x.name for x in test_cases]), file=stderr)
        raise LookupError("Not all test cases have been found")

    # Create records
    for case in test_cases:
        TestCaseSet(test_run=test_run, test_case=case).save()


@db.atomic('EXCLUSIVE')
def add_test_result(testrun_id: int,
                    testcase_name: str,
                    is_passed: bool,
                    date_time: datetime) -> None:
    test_run = TestRun.get_by_id(testrun_id)
    test_case = TestCase.get(name=testcase_name)
    TestResult(test_run=test_run,
               test_case=test_case,
               date_time=date_time,
               is_passed=is_passed).save()


#######################################
# AGGREGATE REQUESTS
#######################################

@db.atomic('EXCLUSIVE')
def get_all_requirements_for_test(testcase: TestCase) -> List[Requirement]:
    links = RequirementToTestCase.select() \
        .where(RequirementToTestCase.test_case == testcase)
    return [x.requirement for x in links]


@db.atomic('EXCLUSIVE')
def get_all_test_results(testrun_id: int) -> List[TestResult]:
    test_run = TestRun.get_by_id(testrun_id)
    return list(TestResult.select().where(TestResult.test_run == test_run))


@db.atomic('EXCLUSIVE')
def get_all_tests_in_set(testrun_or_id: [int, TestRun]) -> List[TestCase]:
    test_run = testrun_or_id if isinstance(testrun_or_id, TestRun) \
        else TestRun.get_by_id(testrun_or_id)
    links = TestCaseSet.select().where(TestCaseSet.test_run == test_run)
    return [x.test_case for x in links]
