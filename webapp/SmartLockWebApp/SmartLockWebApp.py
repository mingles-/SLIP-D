from flask import Flask, render_template, session, flash, request, abort, redirect, url_for
from config import *
from forms import LoginForm, RegisterForm
from base64 import b64encode
from functools import wraps

app = Flask(__name__)
app.secret_key = SECRET_KEY
app.debug = True

#################################
# ========= Bootstrap ========= #
#################################

from flask_bootstrap import Bootstrap

Bootstrap(app)


#################################
# ============ API ============ #
#################################

import requests
from requests import ConnectionError

def api_endpoint(endpoint=''):
    return '{}/{}'.format(API_BASE_ADDR,endpoint)

def auth_headers(username,password):
    return {
        'Authorization': 'Basic ' + b64encode("{}:{}".format(username, password))
    }

#################################
# =========== Views =========== #
#################################

def login_required(function):
    @wraps(function)
    def decorated_function(*args, **kwargs):
        if 'username' in session and 'password' in session and session['username'] and session['password']:
            return function(*args, **kwargs)
        else:
            flash('You need to be logged in to access that page.','danger')
            return redirect(url_for('login', next=url_for(function.__name__)))
    return decorated_function


def login_prohibited(function):
    @wraps(function)
    def decorated_function(*args, **kwargs):
        if 'username' in session and 'password' in session and session['username'] and session['password']:
            flash('Please log out to access that page.','danger')
            return redirect(url_for('profile'))
        else:
            return function(*args, **kwargs)
    return decorated_function


@app.route('/')
def index():
    return render_template('index.htm', app_name=APP_NAME, page='Home')


@app.route('/profile')
@login_required
def profile():
    return render_template('profile.htm', app_name=APP_NAME, page='Home')


@app.route('/login', methods=['GET', 'POST'])
@login_prohibited
def login():

    # Here we use a class of some kind to represent and validate our
    # client-side form data. For example, WTForms is a library that will
    # handle this for us, and we use a custom LoginForm to validate.
    form = LoginForm()
    if form.validate_on_submit():
        # Login and validate the user.
        # user should be an instance of your `User` class

        try:
            response = requests.get(
                api_endpoint('protected-resource'),
                headers=auth_headers(form.email.data, form.password.data)
            )

            if response.status_code == 200:

                flash('Logged in successfully.','success')

                session['username'] = form.email.data
                session['password'] = form.password.data

                next = request.args.get('next')
                # next_is_valid should check if the user has valid
                # permission to access the `next` url
                # if not next_is_valid(next):
                #     return abort(400)

                return redirect(next or url_for('profile'))

            else:
                flash('Login failed. Ensure your e-mail and password are correct and try again.','danger')
        except ConnectionError as ex:
            flash('Failed to connect to login server. Please try again later.', 'danger')
    return render_template('login.html', app_name=APP_NAME, page='Login', form=form)


@app.route('/register', methods=['GET', 'POST'])
@login_prohibited
def register():
    form = RegisterForm(request.form)
    # Validate inputs
    if form.validate_on_submit():
        # Make a new database record

        try:
            response = requests.post(api_endpoint('register'),
                                    data={'email': form.email.data,
                                          'password': form.password.data
                                    }
            )
                
            if response.status_code == 201:
                
                flash('Registered {} successfully! Please log in to continue.'.format(form.email.data),'success')
                
                next = request.args.get('next')
                # next_is_valid should check if the user has valid
                # permission to access the `next` url
                # if not next_is_valid(next):
                #     return abort(400)
                
                return redirect(next or url_for('login'))
            
            elif response.status_code == 406:
                flash('E-mail address already registered, please use a different e-mail address.', 'danger')
            else:
                flash('Status {}: Registration failed, please try again later.'.format(response.status_code), 'danger')
        except ConnectionError as ex:
            flash('Failed to connect to registration server. Please try again later.', 'danger')

    return render_template('register.htm', app_name=APP_NAME, page='Register', form=form)


@app.route('/logout')
def logout():
    session.pop('username',None)
    session.pop('password',None)
    return redirect(url_for('index'))


###########################
# ======== Start ======== #
###########################

if __name__ == '__main__':
    app.run(port=8000)
