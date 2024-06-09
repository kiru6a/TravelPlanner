from flask.helpers import url_for
from sqlalchemy import create_engine, text
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
import os
from unsplash_api import find_city_image
from airports import get_airports_by_city_name

db_connection_string = os.environ["DB_CONNECTION_STRING"]

engine = create_engine(db_connection_string)


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


def insert_user_into_db(username: str, password: str) -> int:
    with engine.connect() as conn:
        stmt = text("INSERT INTO planner_user (username, password) "
                    "VALUES (:username, :password)")
        result = conn.execute(stmt, {"username": username, "password": password})

        conn.commit()
        return result.lastrowid


def fetch_user_by_username(username: str):
    with engine.connect() as conn:
        stmt = text("SELECT user_id, username, password "
                    "FROM planner_user "
                    "WHERE username = :username")
        result = conn.execute(stmt, {"username": username})
        return result.fetchone()


def fetch_user_by_id(user_id: int):
    with engine.connect() as conn:
        stmt = text("SELECT user_id, username, password "
                    "FROM planner_user "
                    "WHERE user_id = :userId")
        result = conn.execute(stmt, {"userId": user_id})
        return result.fetchone()


def fetch_trips_data_by_user_id(user_id: int):
    with engine.connect() as conn:
        stmt = text("SELECT t.trip_id, t.date_from, "
                    "t.date_to, c_from.city_name AS from_name, "
                    "c_to.city_name AS to_name, c_to.city_image_url AS city_to_image "
                    "FROM trips t "
                    "JOIN city c_from ON t.city_from_id = c_from.city_id "
                    "JOIN city c_to ON t.city_to_id = c_to.city_id "
                    "WHERE t.user_id = :userId")
        result = conn.execute(stmt, {"userId": user_id})
        return result.all()


def insert_city_into_db(cityName: str) -> int:
    with engine.connect() as conn:
        stmt = text("INSERT INTO city(city_name, city_image_url) "
                    "VALUES (:cityName, :cityImageUrl)")
        city_image_url = find_city_image(cityName)

        if not city_image_url:
            city_image_url = url_for("static", filename="images/default_city_image.jpeg")

        result = conn.execute(stmt, {"cityName": cityName, "cityImageUrl": city_image_url})
        conn.commit()

        airports_data_list = get_airports_by_city_name(cityName)
        city_id = result.lastrowid

        stmt = text("INSERT INTO airport(airport_code, airport_name, city_id) "
                    "VALUES (:airportCode, :airportName, :cityId)")
        for data in airports_data_list:
            conn.execute(stmt, {"airportCode": data["code"], "airportName": data["name"], "cityId": city_id})
            conn.commit()

        return city_id


def fetch_airports_by_city_id(cityId: int):
    with engine.connect() as conn:
        stmt = text("SELECT airport_code, airport_name "
                    "FROM airport "
                    "WHERE city_id = :cityId")
        result = conn.execute(stmt, {"cityId": cityId})
        return result.all()


def insert_trip_into_db(userId: int, departureCity: str, destinationCity: str,
                        dateFrom: str, dateTo: str):
    with engine.connect() as conn:
        stmt = text("SELECT c.city_id "
                    "FROM city c "
                    "WHERE c.city_name = :cityName")
        result = conn.execute(stmt, {"cityName": departureCity})
        row = result.fetchone()
        departure_city_id = row.city_id if row else insert_city_into_db(departureCity)

        stmt = text("SELECT c.city_id "
                    "FROM city c "
                    "WHERE c.city_name = :cityName")
        result = conn.execute(stmt, {"cityName": destinationCity})
        row = result.fetchone()
        destination_city_id = row.city_id if row else insert_city_into_db(destinationCity)

        stmt = text("INSERT INTO trips(user_id, city_from_id, city_to_id, date_from, date_to) "
                    "VALUES (:userId, :cityFromId, :cityToId, :dateFrom, :dateTo)")

        params = {"userId": userId, "cityFromId": departure_city_id,
                  "cityToId": destination_city_id, "dateFrom": dateFrom,
                  "dateTo": dateTo}
        result = conn.execute(stmt, params)
        conn.commit()

        return result.lastrowid


def fetch_trip_and_city_data_by_trip_id(tripId: int):
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
