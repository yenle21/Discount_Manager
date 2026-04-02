from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import cloudinary


app = Flask(__name__)
#app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:admin%40123@localhost/kidmanagerdb?charset=utf8mb4"
#app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
#db = SQLAlchemy(app)

cloudinary.config(cloud_name='dubbmztca',
                  api_key='317478548846544',
                  api_secret='Z_s6WQbLfUbuWHbyDXALHEpZJr0')


app.secret_key = "fhdjkhgfsh"
#login = LoginManager(app)