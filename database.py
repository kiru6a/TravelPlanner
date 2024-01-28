from sqlalchemy import create_engine, text
from configparser import ConfigParser
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError


config = ConfigParser()
config.read("config.properties")

dbConnectionString = config.get("DEFAULT", "DB_CONNECTION_STRING")

engine = create_engine(dbConnectionString)


class SignupForm(FlaskForm):
  username = StringField(label="Username", validators=[InputRequired(),\
              Length(min=4,max=20)], \
              render_kw={"placeholder": "username"})
  password = PasswordField(label="Password", validators=[InputRequired(),\
                      Length(min=4, max=20)],\
                           render_kw={"placeholder": "password"})
  submit = SubmitField(label="Signup")

  def validate_username(self, username):
    with engine.connect() as conn:
      stmt = text("SELECT username FROM planner_user "\
                  "WHERE username = :username")
      result = conn.execute(stmt, {"username": username.data})
      if result.fetchone():
        raise ValidationError("Username already exists. Please choose another one")

def insertUserIntoDb(username: str, password: str):
  with engine.connect() as conn:
    stmt = text("INSERT INTO planner_user (username, password) "\
                "VALUES (:username, :password)")
    result = conn.execute(stmt, {"username": username, "password": password})
    
    conn.commit()
    return result.lastrowid

  