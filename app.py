from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
import os


app = Flask(__name__)
db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "database.db")
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"

app.config["SECRET_KEY"] = "development_simple_key"


db = SQLAlchemy(app)


class PlannerUser(UserMixin, db.Model):
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(25), nullable=False)
  password = db.Column(db.String(25), nullable=False)

@app.route("/")
def sayHello():
  return render_template("home.html")


@app.route("/trips")
def trips():
  return "trips"


if __name__ == "__main__":
  app.run(host='0.0.0.0', debug=True)
