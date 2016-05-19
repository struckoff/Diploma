from flask import Flask, render_template, request, g, Response, session, abort
from flask_sqlalchemy import SQLAlchemy
from math import isclose
from functools import wraps
import json
import sqlite3

from core.core import test_runner, logger

DATABASE = 'database.db'
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + DATABASE
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'
db = SQLAlchemy(app)


class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String)
    test_cases = db.relationship('TestData')

    def __init__(self, description):
        self.description = description

class TestData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'))
    test = db.Column(db.String)
    expect = db.Column(db.String)
    case_id = db.Column(db.Integer)

    def __init__(self, id, room_id, test, expect):
        self.case_id = id
        self.room_id = room_id
        self.test = test
        self.expect = expect

def check_auth(password):
    """This function is called to check if a username /
    password combination is valid.
    """
    return password == 'admin'

def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        logger.debug(request.form)
        if session.get('password') is not None:
            if request.form.get('logout') is not None or not check_auth(session['password']):
                session.pop('password', None)
            else:
                return f(*args, **kwargs)
        else:
            if request.method == 'POST' and check_auth(request.form.get('password')):
                session['password'] = request.form.get('password')
                return f(*args, **kwargs)
        return render_template('main_ui/password.html')
    return decorated


@app.before_request
def before_request():
    g.db = sqlite3.connect(DATABASE)
    db.create_all()

@app.after_request
def after_request(response):
    g.db.close()
    return response

@app.route('/')
def index():
    return render_template('main_ui/index.html')


@app.route('/room/<room_id>')
def test_room(room_id):
    room = Room.query.filter_by(id=room_id).first()
    if room is None:
        return abort(404)
    if not request.is_xhr:
        return render_template('main_ui/test.html', room_id=room_id)
    else:
        code = request.args.get('text', '')
        tests = tuple(case.test for case in room.test_cases)
        expects = tuple(case.expect for case in room.test_cases)
        results = test_runner(code, tests, expects)
        ratio = len([r for r in results if r["state"]])/len(results) * 100
        stats = {
            "ratio": round(ratio),
            "style": "success" if isclose(ratio, 100) else "warning" if ratio > 10 else "danger"
        }
        return json.dumps({"results": results, "statistic":stats})

@app.route('/create')
def create_test():
    if request.is_xhr:
        room = Room(request.args.get('description', ''))
        db.session.add(room)
        db.session.commit()
        for key, case in json.loads(request.args.get('cases', '{}')).items():
            tests = case.get("tests", "")
            expects = case.get("expects", "")
            id = case.get("id", 0)
            testdata = TestData(id, room.id, tests, expects)
            db.session.add(testdata)
        db.session.commit()
        return json.dumps({"url": '/edit/{}'.format(room.id)})
    else:
        return render_template('main_ui/create_test.html', isnew=True)


@app.route('/edit/<room_id>', methods=['GET', 'POST'])
@requires_auth
def edit_test(room_id):
    room = Room.query.filter_by(id=room_id).first()
    if room is None:
        return abort(404)
    if request.is_xhr:
        if request.args.get("description") is not None \
                and request.args.get("description", False) != room.description:
            room.description = request.args.get("description")
        if request.args.get("cases") is not None:
            room.test_cases[:] = []
            logger.debug(request.args["cases"])
            for key, case in json.loads(request.args["cases"]).items():
                testdata = TestData(case["id"], room_id, case["tests"], case["expects"])
                db.session.add(testdata)

        db.session.commit()
        logger.debug(room.test_cases)

        return json.dumps({
            "description": room.description,
            "cases": [{
                          "id": c.case_id,
                          "tests": c.test,
                          "expects": c.expect
                      } for c in room.test_cases]
        })

    return render_template('main_ui/create_test.html', isnew=False, room_id=room_id)

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
        logger.debug({"results": results, "statistic":stats})
        return json.dumps({"results": results, "statistic":stats})

if __name__ == '__main__':
    app.run(port=8000, debug=True)
