from flask_sqlalchemy import SQLAlchemy

from main import app

DB = SQLAlchemy(app)

successful_tests = DB.Table('successful_tests',
                            DB.Column('report_id',
                                      DB.Integer,
                                      DB.ForeignKey('report.id'),
                                      nullable=False),
                            DB.Column('testdata_id',
                                      DB.Integer,
                                      DB.ForeignKey('testdata.id'),
                                      nullable=False),
                            DB.PrimaryKeyConstraint('report_id', 'testdata_id'))

failed_tests = DB.Table('failed_tests',
                        DB.Column('report_id',
                                  DB.Integer,
                                  DB.ForeignKey('report.id'),
                                  nullable=False),
                        DB.Column('testdata_id',
                                  DB.Integer,
                                  DB.ForeignKey('testdata.id'),
                                  nullable=False),
                        DB.PrimaryKeyConstraint('report_id', 'testdata_id'))

class Room(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)
    description = DB.Column(DB.String)
    password = DB.Column(DB.String, default="")
    test_cases = DB.relationship('TestData')
    reports = DB.relationship('Report')
    is_network = DB.Column(DB.Boolean)
    timeout = DB.Column(DB.Integer)

    def __init__(self, description, password):
        self.description = description
        self.password = password


class TestData(DB.Model):
    __tablename__ = 'testdata'
    id = DB.Column(DB.Integer, primary_key=True)
    room_id = DB.Column(DB.Integer, DB.ForeignKey('room.id'))
    test = DB.Column(DB.String)
    expect = DB.Column(DB.Integer)
    got = DB.Column(DB.Integer)
    case_id = DB.Column(DB.Integer)


    def __init__(self, id, room_id, test, expect, got=''):
        self.case_id = id
        self.room_id = room_id
        self.test = test
        self.expect = expect
        self.got = got

    def set_got(self, got):
        self.got = got

class ReportTestData(DB.Model):
    __tablename__ = 'reporttestdata'
    report_id = DB.Column(DB.Integer, DB.ForeignKey('report.id'))
    id = DB.Column(DB.Integer, primary_key=True)
    test = DB.Column(DB.String)
    expect = DB.Column(DB.Integer)
    got = DB.Column(DB.Integer)
    case_id = DB.Column(DB.Integer)
    state = DB.Column(DB.Boolean)

    def __init__(self, id, report_id, test, expect, got, state):
        self.case_id = id
        self.report_id = report_id
        self.test = test
        self.expect = expect
        self.got = got
        self.state = state

class Report(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)
    room_id = DB.Column(DB.Integer, DB.ForeignKey('room.id'))
    name = DB.Column(DB.String)
    comment = DB.Column(DB.String)
    code = DB.Column(DB.String)
    # passed = DB.relationship('TestData', secondary=successful_tests, backref='passed')
    # failed = DB.relationship('TestData', secondary=failed_tests, backref='failed')
    cases = DB.relationship('ReportTestData')

    def __init__(self, room_id, name, code, comment=''):
        self.room_id = room_id
        self.name = name
        self.comment = comment
        self.code = code
