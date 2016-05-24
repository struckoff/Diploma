from flask_sqlalchemy import SQLAlchemy

from main import app

DB = SQLAlchemy(app)


class Room(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)
    description = DB.Column(DB.String)
    password = DB.Column(DB.String, default="")
    test_cases = DB.relationship('TestData')

    def __init__(self, description, password):
        self.description = description
        self.password = password


class TestData(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)
    room_id = DB.Column(DB.Integer, DB.ForeignKey('room.id'))
    test = DB.Column(DB.String)
    expect = DB.Column(DB.String)
    case_id = DB.Column(DB.Integer)

    def __init__(self, id, room_id, test, expect):
        self.case_id = id
        self.room_id = room_id
        self.test = test
        self.expect = expect
