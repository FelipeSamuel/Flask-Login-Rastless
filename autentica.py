from flask import Flask, request
from flask_login import current_user, login_user, logout_user, LoginManager, UserMixin
from flask_restless import APIManager, ProcessingException
from flask_sqlalchemy import SQLAlchemy
import os


# Step 1: setup the Flask application.
app = Flask(__name__)
app.config['DEBUG'] = True
app.config['TESTING'] = True
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///login.db'

# Step 2: initialize extensions.
db = SQLAlchemy(app)
api_manager = APIManager(app, flask_sqlalchemy_db=db)
login_manager = LoginManager()
login_manager.setup_app(app)


# Step 3: create the user database model.
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Unicode)
    password = db.Column(db.Unicode)


# Step 4: create the database and add a test user.
db.create_all()
user1 = User(username=u'example', password=u'example')
db.session.add(user1)
db.session.commit()


# Step 5: this is required for Flask-Login.
@login_manager.user_loader
def load_user(userid):
    return User.query.get(userid)


# Step 8: create the API for User with the authentication guard.
def auth_func(**kw):
    if not current_user.is_authenticated:
        raise ProcessingException(description='Not Authorized', code=401)

api_manager.create_api(User,methods=['POST','GET'], preprocessors=dict(POST=[auth_func], GET_SINGLE=[auth_func], GET_MANY=[auth_func]))

@app.route('/login', methods=['POST', 'GET'])
@app.route('/', methods=['POST', 'GET'])
def login():
    username = request.args.get('username')
    password = request.args.get('password')

    matches = User.query.filter_by(username=username,password=password).all()
    if len(matches) > 0:
        login_user(matches[0])
        return 'logado'
    return 'erro'


@app.route('/logout')
def logout():
    logout_user()
    return 'deslogado'

app.run()
