# flask_app/app.py
# FLASK_APP=app flask run --with-threads
# python pywsgi.py

from flask import Flask
from model.db import init_db


app = Flask(__name__)


@app.route('/hello-world')
def hello_world():
    return 'Hello, World!'


if __name__ == '__main__':
    init_db(app)
    app.run()