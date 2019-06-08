import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from ChatRoom.db import get_db

bp = Blueprint('user', __name__, url_prefix='/user')


@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        user_name = request.form['username']
        password = request.form['password']
        email = request.form['email']
        db = get_db()
        error = None

        if not user_name:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif not email:
            error = 'Email is required.'
        elif db.execute(
            'SELECT UserID FROM USER WHERE UserName = ?', (user_name,)
        ).fetchone() is not None:
            error = 'User {} is already registered.'.format(user_name)

        if error is None:
            db.execute(
                'INSERT INTO USER (UserName, Password, Email) VALUES (?, ?, ?)',
                (user_name, generate_password_hash(password), email)
            )
            db.commit()
            return redirect(url_for('user.login'))

        flash(error)

    return render_template('user/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        user_name = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM USER WHERE UserName = ?', (user_name,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('user/login.html')

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM USER WHERE UserID = ?', (user_id,)
        ).fetchone()


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('user.login'))

        return view(**kwargs)

    return wrapped_view
