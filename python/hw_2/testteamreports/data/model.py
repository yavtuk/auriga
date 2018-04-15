from os import path
import peewee as pw

from testteamreports.settings import DATABASE_FILE

# Initialize DB in current directory
db_path = path.join(path.abspath(path.dirname(__file__)), DATABASE_FILE)
db = pw.SqliteDatabase(db_path)


class BaseModel(pw.Model):
    class Meta:
        database = db


class UserRecord(BaseModel):
    login = pw.CharField(unique=True)
    pwd_hash = pw.CharField()


class Requirement(BaseModel):
    name = pw.CharField(unique=True)
    risk = pw.IntegerField(default=1)


class TestCase(BaseModel):
    name = pw.CharField(unique=True)


class RequirementToTestCase(BaseModel):
    requirement = pw.ForeignKeyField(Requirement)
    test_case = pw.ForeignKeyField(TestCase)


class TestRun(BaseModel):
    description = pw.CharField()
    start_date = pw.DateField()
    end_date = pw.DateField()


class TestCaseSet(BaseModel):
    test_run = pw.ForeignKeyField(TestRun)
    test_case = pw.ForeignKeyField(TestCase)


class TestResult(BaseModel):
    date_time = pw.DateTimeField()
    test_case = pw.ForeignKeyField(TestCase)
    test_run = pw.ForeignKeyField(TestRun)
    is_passed = pw.BooleanField()


all_tables = [UserRecord, Requirement, TestCase, TestRun,
              RequirementToTestCase, TestCaseSet, TestResult]
