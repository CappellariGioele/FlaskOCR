import os
from flask import Flask
from flask_migrate import Migrate
from flask_login import LoginManager
from dotenv import load_dotenv
from routes.ocr import ocr as bp_ocr
from routes.auth import auth as bp_auth
from routes.base import base as bp_base
from models.conn import db
from models.models import *
from utils.init_functions import init_structure

load_dotenv()

app = Flask(__name__)

# Configurazioni applicazione
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACE_MODIFICATIONS'] = False

# Blueprints
app.register_blueprint(bp_base)
app.register_blueprint(bp_ocr, url_prefix='/api/ocr')
app.register_blueprint(bp_auth, url_prefix='/auth')

# DB
db.init_app(app)
migrate = Migrate(app, db)

# Autenticazione (LoginManager)
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    stmt = db.select(User).filter_by(id=user_id)
    user = db.session.execute(stmt).scalar_one_or_none()
    return user

if __name__ == '__main__':
    with app.app_context():
        init_structure()
    app.run(debug=True)
