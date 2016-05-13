from flask import Flask, render_template, request, g
from flask_sqlalchemy import SQLAlchemy
from math import isclose
import json
import sqlite3

from core.core import test_runner

DATABASE = 'database.db'
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + DATABASE
db = SQLAlchemy(app)


class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String)

    def __init__(self, description):
        self.description = description

class TestData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'))
    test = db.Column(db.String)
    expect = db.Column(db.String)
    case_id_in_room = db.Column(db.Integer)

    def __init__(self, case_id, room_id, test, expect):
        self.case_id_in_room = case_id
        self.room_id = room_id
        self.test = test
        self.expect = expect


@app.before_request
def before_request():
    g.db = sqlite3.connect(DATABASE)
    db.create_all()

@app.after_request
def after_request(response):
    g.db.close()
    return response

@app.route('/hw')
def hello_world():
    return 'Hello World!'

@app.route('/<room_id>')
def index(room_id):

    if not request.is_xhr:
        return render_template('main_ui/test.html')
    else:
        room = Room.query.filter_by(id=room_id).first()
        cases = TestData.query.filter_by(room_id=room_id).all()
        code = request.args.get('text', '')
        print([(case.test, case.expect) for case in cases])
        expects = [1, 2, 3, 4, 5]
        tests = [(1, 1), (1, 1), (1, 1), (3, 1), (2, 3)]
        expects=[2] * 5
        results = test_runner(code, tests, expects)
        ratio = len([r for r in results if r["state"]])/len([*zip(expects, tests)]) * 100
        stats = {
            "ratio": ratio,
            "style": "success" if isclose(ratio, 100) else "warning" if ratio > 10 else "danger"
        }
        print({"results": results, "statistic":stats})
        return json.dumps({"results": results, "statistic":stats})

@app.route('/create')
def create_test():
    if request.is_xhr:
        room = Room(request.args.get('description', ''))
        print(request.args)
        db.session.add(room)
        db.session.commit()
        for key, val in json.loads(request.args.get('cases', '{}')).items():
            tests = val.get("tests", "")
            expects = val.get("expects", "")

            testdata = TestData(key, room.id, tests, expects)
            db.session.add(testdata)
        db.session.commit()
        print(room.id)
        return json.dumps({"url": '/edit/{}'.format(room.id)})
    else:
        return render_template('main_ui/create_test.html', isnew=True)


@app.route('/edit/<room_id>')
def edit_test(room_id):
    if request.is_xhr:
        room = Room.query.filter_by(id=room_id).first()
        cases = TestData.query.filter_by(room_id=room_id).all()
        print(request.args)
        if request.args.get("description") is not None \
                and request.args.get("description", False) != room.description:
            room.description = request.args.get("description")
        if request.args.get("cases", False):
            for key, case in json.loads(request.args["cases"]).items():
                case_original = TestData.query.filter_by(id=case['id']).first()
                if case_original.test != case["tests"]:
                    case_original.test = case["tests"]
                if case_original.expect != case["expects"]:
                    case_original.expect = case["expects"]
        db.session.commit()

        return json.dumps({
                              "description": room.description,
                              "cases": [{
                                  "id": c.id,
                                  "tests": c.test,
                                  "expects": c.expect
                              } for c in cases]
        })

    return render_template('main_ui/create_test.html', isnew=False)

@app.route('/sel', methods=['GET', 'POST'])
def sel():
    if not request.is_xhr:
        return render_template('main_ui/test.html')
    else:
        code = request.args.get('text', '')
        expects = [1, 2, 3, 4, 5]
        tests = [(1, 1), (1, 1), (1, 1), (3, 1), (2, 3)]
        expects=[2] * 5
        results = test_runner(code, tests, expects)
        ratio = len([r for r in results if r["state"]])/len([*zip(expects, tests)]) * 100
        stats = {
            "ratio": ratio,
            "style": "success" if isclose(ratio, 100) else "warning" if ratio > 10 else "danger"
        }
        print({"results": results, "statistic":stats})
        return json.dumps({"results": results, "statistic":stats})

if __name__ == '__main__':
    app.run(port=8000, debug=True)
