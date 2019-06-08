import os
from flask import Flask, redirect, url_for, render_template
from . import db
from . import user
from werkzeug.security import generate_password_hash


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'ChatRoom.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, Flask!'

    # init db.USER
    @app.route('/init-db-user')
    def init_db_user():
        my_db = db.get_db()
        my_db.execute(
            'INSERT INTO USER (UserName, Password, Email) VALUES (?, ?, ?)',
            ('Admin', generate_password_hash('123'), 'admin2@test.com')
        )
        my_db.execute(
            'INSERT INTO USER (UserName, Password, Email) VALUES (?, ?, ?)',
            ('Admin2', generate_password_hash('123'), 'admin2@test.com')
        )
        my_db.execute(
            'INSERT INTO USER (UserName, Password, Email) VALUES (?, ?, ?)',
            ('User01', generate_password_hash('123'), 'user01@test.com')
        )
        my_db.execute(
            'INSERT INTO USER (UserName, Password, Email) VALUES (?, ?, ?)',
            ('User02', generate_password_hash('123'), 'user02@test.com')
        )
        my_db.commit()
        print('Add four user sucessfully.')
        return redirect(url_for('user.register'))

    @app.route('/index')
    def index():
        return render_template('index.html')

    db.init_app(app)

    app.register_blueprint(user.bp)

    return app
