from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import cloudinary


app = Flask(__name__)
<<<<<<< HEAD
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:admin%40123@localhost/discountdb?charset=utf8mb4"
=======
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:admin%40123@localhost/voucherdb?charset=utf8mb4"
>>>>>>> 893d5ed7924071a573d8a43ef4dd187172844816
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
db = SQLAlchemy(app)

cloudinary.config(cloud_name='dubbmztca',
                  api_key='317478548846544',
                  api_secret='Z_s6WQbLfUbuWHbyDXALHEpZJr0')


app.secret_key = "fhdjkhgfsh"
<<<<<<< HEAD
login = LoginManager(app)

@login.user_loader          # ← dòng này có chưa?
def load_user(user_id):
    return None
=======
#login = LoginManager(app)
>>>>>>> 893d5ed7924071a573d8a43ef4dd187172844816
