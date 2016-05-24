from flask import  render_template, request, g, session, abort, Markup
from functools import wraps
import json
import sqlite3

from main import app, DATABASE
from database import Room, TestData, DB
from core.core import test_runner, logger



def check_auth(password):
    """This function is called to check if a username /
    password combination is valid.
    """
    return password == 'admin'


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
    DB.create_all()

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
        return render_template('main_ui/test.html',
                               room_id=room_id,
                               description=Markup(room.description))
    else:
        code = request.args.get('text', '')
        tests = tuple(case.test for case in room.test_cases)
        expects = tuple(case.expect for case in room.test_cases)
        results = test_runner(code, tests, expects)
        ratio = len([r for r in results if r["state"]])/len(results) * 100
        return json.dumps({"results": results, "ratio": round(ratio)})


@app.route('/create')
def create_test():
    if request.is_xhr:
        room = Room(request.args.get('description', ''))
        DB.session.add(room)
        DB.session.commit()
        for key, case in json.loads(request.args.get('cases', '{}')).items():
            tests = case.get("tests", "")
            expects = case.get("expects", "")
            id = case.get("id", 0)
            testdata = TestData(id, room.id, tests, expects)
            DB.session.add(testdata)
        DB.session.commit()
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
                DB.session.add(testdata)

        DB.session.commit()

        return json.dumps({
            "description": room.description,
            "cases": [{
                          "id": c.case_id,
                          "tests": c.test,
                          "expects": c.expect
                      } for c in room.test_cases]
        })

    return render_template('main_ui/create_test.html', isnew=False, room_id=room_id)