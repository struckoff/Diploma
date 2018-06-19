import sys
import os
from flask import Flask

DATABASE = 'database.db'
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + DATABASE
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['STUDENTTESTER_CHROMECON'] = os.getenv('STUDENTTESTER_CHROMECON', '127.0.0.9222')
app.config['STUDENTTESTER_MAXTABS'] = int(os.getenv('STUDENTTESTER_MAXTABS', 20))
app.config['STUDENTTESTER_MAXTIMEOUT'] = int(os.getenv('STUDENTTESTER_MAXTIMEOUT', 300))

from views import *

if __name__ == '__main__':
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    else:
        port = 80
    app.run(host='0.0.0.0', port=port, debug=True)
