from flask.helpers import url_for
from sqlalchemy import create_engine, text
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
import os
from unsplash_api import findCityImage
from airports import getAirportsByCityName

dbConnectionString = os.environ["DB_CONNECTION_STRING"]

engine = create_engine(dbConnectionString)


class SignupForm(FlaskForm):
    username = StringField(label="Username", validators=[InputRequired(),
                                                         Length(min=4, max=20)],
                           render_kw={"placeholder": "username"})
    password = PasswordField(label="Password", validators=[InputRequired(),
                                                           Length(min=4, max=20)],
                             render_kw={"placeholder": "password"})
    submit = SubmitField(label="Signup")

    def validate_username(self, username: str):
        with engine.connect() as conn:
            stmt = text("SELECT username FROM planner_user "
                        "WHERE username = :username")
            result = conn.execute(stmt, {"username": username.data})
            if result.fetchone():
                raise ValidationError("Username already exists. Please choose another one")


class LoginForm(FlaskForm):
    username = StringField(label="Username", validators=[InputRequired(), \
                                                         Length(min=4, max=20)], \
                           render_kw={"placeholder": "username"})
    password = PasswordField(label="Password", validators=[InputRequired(), \
                                                           Length(min=4, max=20)], \
                             render_kw={"placeholder": "password"})
    submit = SubmitField(label="Login")


def insertUserIntoDb(username: str, password: str) -> int:
    with engine.connect() as conn:
        stmt = text("INSERT INTO planner_user (username, password) "
                    "VALUES (:username, :password)")
        result = conn.execute(stmt, {"username": username, "password": password})

        conn.commit()
        return result.lastrowid


def fetchUserByUsername(username: str):
    with engine.connect() as conn:
        stmt = text("SELECT user_id, username, password "
                    "FROM planner_user "
                    "WHERE username = :username")
        result = conn.execute(stmt, {"username": username})
        return result.fetchone()


def fetchUserById(userId: int):
    with engine.connect() as conn:
        stmt = text("SELECT user_id, username, password "
                    "FROM planner_user "
                    "WHERE user_id = :userId")
        result = conn.execute(stmt, {"userId": userId})
        return result.fetchone()


def fetchTripsDataByUserId(userId: int):
    with engine.connect() as conn:
        stmt = text("SELECT t.trip_id, t.date_from, "
                    "t.date_to, c_from.city_name AS from_name, "
                    "c_to.city_name AS to_name, c_to.city_image_url AS city_to_image "
                    "FROM trips t "
                    "JOIN city c_from ON t.city_from_id = c_from.city_id "
                    "JOIN city c_to ON t.city_to_id = c_to.city_id "
                    "WHERE t.user_id = :userId")
        result = conn.execute(stmt, {"userId": userId})
        return result.all()


def insertCityIntoDb(cityName: str) -> int:
    with engine.connect() as conn:
        stmt = text("INSERT INTO city(city_name, city_image_url) "
                    "VALUES (:cityName, :cityImageUrl)")
        cityImageUrl = findCityImage(cityName)

        if not cityImageUrl:
            cityImageUrl = url_for("static", filename="images/default_city_image.jpeg")

        result = conn.execute(stmt, {"cityName": cityName, "cityImageUrl": cityImageUrl})
        conn.commit()

        airportsDataList = getAirportsByCityName(cityName)
        cityId = result.lastrowid

        stmt = text("INSERT INTO airport(airport_code, airport_name, city_id) "
                    "VALUES (:airportCode, :airportName, :cityId)")
        for data in airportsDataList:
            conn.execute(stmt, {"airportCode": data["code"], "airportName": data["name"], "cityId": cityId})
            conn.commit()

        return cityId


def fetchAirportsByCityId(cityId: int):
    with engine.connect() as conn:
        stmt = text("SELECT airport_code, airport_name "
                    "FROM airport "
                    "WHERE city_id = :cityId")
        result = conn.execute(stmt, {"cityId": cityId})
        return result.all()


def insertTripIntoDb(userId: int, departureCity: str, destinationCity: str,
                     dateFrom: str, dateTo: str):
    with engine.connect() as conn:
        stmt = text("SELECT c.city_id "
                    "FROM city c "
                    "WHERE c.city_name = :cityName")
        result = conn.execute(stmt, {"cityName": departureCity})
        row = result.fetchone()
        departureCityId = row.city_id if row else insertCityIntoDb(departureCity)

        stmt = text("SELECT c.city_id "
                    "FROM city c "
                    "WHERE c.city_name = :cityName")
        result = conn.execute(stmt, {"cityName": destinationCity})
        row = result.fetchone()
        destinationCityId = row.city_id if row else insertCityIntoDb(destinationCity)

        stmt = text("INSERT INTO trips(user_id, city_from_id, city_to_id, date_from, date_to) "
                    "VALUES (:userId, :cityFromId, :cityToId, :dateFrom, :dateTo)")

        params = {"userId": userId, "cityFromId": departureCityId,
                  "cityToId": destinationCityId, "dateFrom": dateFrom,
                  "dateTo": dateTo}
        result = conn.execute(stmt, params)
        conn.commit()

        return result.lastrowid


def fetchTripAndCityDataByTripId(tripId: int):
    with engine.connect() as conn:
        stmt = text("SELECT t.date_from, t.date_to, "
                    "c_from.city_name AS from_name, "
                    "c_to.city_image_url AS to_image, "
                    "c_from.city_id AS from_id, "
                    "c_to.city_name AS to_name, c_to.city_id AS to_id "
                    "FROM trips t "
                    "JOIN city c_from ON t.city_from_id = c_from.city_id "
                    "JOIN city c_to ON t.city_to_id = c_to.city_id "
                    "WHERE t.trip_id = :tripId")
        result = conn.execute(stmt, {"tripId": tripId})
        return result.fetchone()
