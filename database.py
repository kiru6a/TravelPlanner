from sqlalchemy import create_engine, text
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
import os
from unsplash_api import findCityImage


dbConnectionString = os.environ["DB_CONNECTION_STRING"]

engine = create_engine(dbConnectionString)


class SignupForm(FlaskForm):
  username = StringField(label="Username", validators=[InputRequired(),\
              Length(min=4,max=20)], \
              render_kw={"placeholder": "username"})
  password = PasswordField(label="Password", validators=[InputRequired(),\
                      Length(min=4, max=20)],\
                           render_kw={"placeholder": "password"})
  submit = SubmitField(label="Signup")

  def validate_username(self, username: str):
    with engine.connect() as conn:
      stmt = text("SELECT username FROM planner_user "\
                  "WHERE username = :username")
      result = conn.execute(stmt, {"username": username.data})
      if result.fetchone():
        raise ValidationError("Username already exists. Please choose another one")


class LoginForm(FlaskForm):
  username = StringField(label="Username", validators=[InputRequired(),\
              Length(min=4,max=20)], \
              render_kw={"placeholder": "username"})
  password = PasswordField(label="Password", validators=[InputRequired(),\
                      Length(min=4, max=20)],\
                           render_kw={"placeholder": "password"})
  submit = SubmitField(label="Login")



def insertUserIntoDb(username: str, password: str) -> int:
  with engine.connect() as conn:
    stmt = text("INSERT INTO planner_user (username, password) "\
                "VALUES (:username, :password)")
    result = conn.execute(stmt, {"username": username, "password": password})
    
    conn.commit()
    return result.lastrowid

def fetchUserByUsername(username: str):
  with engine.connect() as conn:
    stmt = text("SELECT user_id, username, password "\
                "FROM planner_user "\
                "WHERE username = :username")
    result = conn.execute(stmt, {"username": username})
    return result.fetchone()

def fetchUserById(userId: int):
  with engine.connect() as conn:
    stmt = text("SELECT user_id, username, password "\
                "FROM planner_user "\
                "WHERE user_id = :userId")
    result = conn.execute(stmt, {"userId": userId})
    return result.fetchone()

def fetchTripsDataByUserId(userId: int):
  with engine.connect() as conn:
    stmt = text("SELECT t.trip_id, t.date_from, "\
              "t.date_to, c.city_name, c.city_image_url "\
              "FROM trips t JOIN city c ON t.city_id = c.city_id "\
              "WHERE t.user_id = :userId")
    result = conn.execute(stmt, {"userId": userId})
    return result.all()

def insertCityIntoDb(cityName: str) -> int:
  with engine.connect() as conn:
    stmt = text("INSERT INTO city(city_name, city_image_url) "\
                "VALUES (:cityName, :cityImageUrl)")
    cityImageUrl = findCityImage(cityName)
    
    result = conn.execute(stmt, {"cityName": cityName, "cityImageUrl": cityImageUrl})
    conn.commit()
    
    return result.lastrowid

def insertTripIntoDb(userId: int, cityName: str, dateFrom: str, dateTo: str):
  with engine.connect() as conn:
    stmt = text("SELECT c.city_id "\
                "FROM city c "\
                "WHERE c.city_name = :cityName")
    result = conn.execute(stmt, {"cityName": cityName})
    row = result.fetchone()

    cityId = row.city_id if row else insertCityIntoDb(cityName)

    stmt = text("INSERT INTO trips(user_id, city_id, date_from, date_to) "\
                "VALUES (:userId, :cityId, :dateFrom, :dateTo)")
    params = {"userId": userId, "cityId": cityId,\
              "dateFrom": dateFrom, "dateTo": dateTo}
    result = conn.execute(stmt, params)
    conn.commit()

    return result.lastrowid

