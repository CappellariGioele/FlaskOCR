import uuid
from flask import Blueprint
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import flash
from flask import make_response
from flask_login import login_user
from flask_login import logout_user
from flask_login import login_required
from models.models import User
from models.conn import db


auth = Blueprint('auth', __name__)


@auth.route('/signup')	
def signup():
	return render_template('auth/signup.html')


@auth.route('/signup', methods=['POST'])
def signup_post():
    username = request.form["username"]
    email = request.form["email"]    
    password = request.form["password"]

    if not username:
        flash('Username invalido!')
        return redirect(url_for('auth.signup'))
    if not email:
        flash('Email invalido!')
        return redirect(url_for('auth.signup'))
    if not password:
        flash('Password invalida!')
        return redirect(url_for('auth.signup'))                
    
    # controllo ser esiste un utente nel db
    user = User.query.filter_by(email=email).first()
    if user: 
        flash('Esiste già un utente con questo email!')
        return redirect(url_for('auth.signup'))

    user = User(username=username, email=email)
    user.set_password(password)  # Imposta la password criptata

    # creazione api key dell'utente
    api_key = str(uuid.uuid4())
    user.set_api_key(api_key)

    db.session.add(user)
    db.session.commit()

    return redirect(url_for('auth.login'))


@auth.route('/login')
def login():
    return render_template('auth/login.html')


@auth.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        flash('Credenziali errate!')
        return redirect(url_for('auth.login')) 

    login_user(user, remember=remember)

    response = make_response(redirect(url_for('base.home')))
    response.set_cookie(
        "api_key", 
        user.get_api_keys().first().value,
        secure=True, 
        samesite="Strict"
    )

    return response


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
