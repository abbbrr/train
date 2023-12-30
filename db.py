from flask_pymongo import PyMongo
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb://localhost:27017/abbbr_base'
mongo = PyMongo(app)
