from flask import Flask

DATABASE = 'database.db'
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + DATABASE
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'

from views import *

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
