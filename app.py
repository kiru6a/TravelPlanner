"""
app.py - Flask Application for Trip Management

This Flask application is designed for managing user trips, including user registration, login, trip creation,
and retrieval of trip details. It utilizes various dependencies for web development, user authentication, and
external APIs for travel-related information.

Dependencies:
    - Flask: Web framework for building the application.
    - Flask-Bcrypt: Used for password hashing.
    - Flask-Login: Manages user sessions and authentication.
    - database.py: Module containing database-related functions.
    - places_api.py: Module for interacting with a places API for city predictions and sights.
    - kiwi_api.py: Module for interacting with the Kiwi API for flight search.

Routes:
    - "/" (home): Renders the home page.
    - "/trips": Placeholder route for future functionality related to trips.
    - "/signup": Allows users to register for the application.
    - "/login": Handles user login and redirects to the user's trips.
    - "/logout": Logs the user out and redirects to the home page.
    - "/trips/<int:userId>": Renders the trips page for a specific user.
    - "/trip/<int:tripId>": Renders detailed information about a specific trip.
    - "/get_city_predictions": Retrieves city predictions based on user input.
    - "/create-trip": Creates a new trip based on user input.
    - "/find_plane_tickets": Finds plane tickets using the Kiwi API.

Note: Ensure that the necessary dependencies are installed and the database is properly set up before running the application.

Usage:
    - Run the application using `python app.py`.
    - Access the application through a web browser at http://127.0.0.1:5000/ by default.
    - Follow the provided routes to register, log in, create trips, and explore trip details.

Author: Kyrylo Vorobiov
"""
from flask import Flask, render_template, flash, redirect, url_for, request, jsonify
from database import SignupForm, insertUserIntoDb, LoginForm, fetchUserByUsername, \
    fetchUserById, fetchTripsDataByUserId, insertTripIntoDb, fetchTripAndCityDataByTripId, fetchAirportsByCityId
from flask_bcrypt import check_password_hash, bcrypt
from flask_login import UserMixin, login_user, logout_user, LoginManager, login_required, current_user
from places_api import getCityPredictions, getCitySights
from kiwi_api import searchForTrips

app = Flask(__name__)
app.config['SECRET_KEY'] = 'development_mock_secret_key'
login_manager = LoginManager(app)


@app.route("/")
def home():
    isAuthenticated = current_user.is_authenticated
    return render_template("home.html", isAuthenticated=isAuthenticated)


@app.route("/trips")
def trips():
    return "trips"


@app.route("/signup", methods=["GET", "POST"])
def signup():
    """
  Handles user registration.

  This function renders the signup page, processes form submissions, and inserts user data
  into the database upon successful registration.

  Returns:
      If the form submission is successful, the function redirects to the login page.
      Otherwise, it renders the signup page with error messages.

  Note:
      This function relies on the SignupForm class from the database module.
  """
    if current_user.is_authenticated:
        return redirect(url_for("logout"))
    form = SignupForm()
    if form.validate_on_submit():
        plainPassword = form.password.data
        pwhash = bcrypt.hashpw(plainPassword.encode('utf8'), bcrypt.gensalt())

        hashedPassword = pwhash.decode()

        insertedId = insertUserIntoDb(form.username.data, hashedPassword)
        flash(f"User successfully registered with ID: {insertedId}", "success")
        return redirect("login")
    else:
        print(form.errors)
    return render_template("signup.html", form=form)


@app.route("/trips/<int:userId>")
@login_required
def tripsForUser(userId):
    """
  Renders the trips page for a specific user.

  This route function retrieves trip records for the specified user from the database
  and transforms them into a list of dictionaries for rendering in the template.

  Parameters:
      userId (int): The user ID for whom the trips are to be displayed.

  Returns:
      If the current user is not authenticated or is not the specified user, the function
      redirects to the logout page. Otherwise, it renders the trips.html template with the
      list of dictionaries containing trip details.

  Note:
      - This function relies on the fetchTripsDataByUserId function from the database module.
      - The trips.html template is used for rendering the page.
  """
    if current_user.id != userId:
        return redirect(url_for("logout"))

    tripsRecords = fetchTripsDataByUserId(userId)
    tripsListOfDicts = []
    for trip in tripsRecords:
        tempDict = {"trip_id": trip.trip_id,
                    "date_from": trip.date_from,
                    "date_to": trip.date_to,
                    "city_from_name": trip.from_name,
                    "city_to_name": trip.to_name,
                    "city_to_image": trip.city_to_image}

        tripsListOfDicts.append(tempDict)

    return render_template("trips.html", trips=tripsListOfDicts)


@app.route("/login", methods=["GET", "POST"])
def login():
    """
  Handles user login.

  This route function renders the login page, processes form submissions, and logs in the user
  if the provided credentials are valid. Upon successful login, the user is redirected to their
  trips page.

  Returns:
      If the user is already authenticated, redirects to the user's trips page.
      If the form submission is successful, logs in the user and redirects to their trips page.
      Otherwise, renders the login page with error messages.

  Note:
      - This function relies on the LoginForm class from the database module.
      - The login_user function is used for managing user sessions.
      - The fetchUserByUsername function is used to retrieve user records from the database.
      - The check_password_hash function is used for password validation.
      - The tripsForUser route is redirected to upon successful login.
  """
    if current_user.is_authenticated:
        return redirect(url_for("tripsForUser", userId=current_user.id))
    form = LoginForm()
    if form.validate_on_submit():
        userRecord = fetchUserByUsername(form.username.data)
        if userRecord and check_password_hash(userRecord.password, form.password.data):
            user = UserMixin()
            user.id = userRecord.user_id
            user.username = userRecord.username
            user.password = userRecord.password

            login_user(user)

            flash(f"Welcome back, {userRecord.username}", "success")
            return redirect(f"trips/{userRecord.user_id}")

    return render_template("login.html", form=form)


@login_manager.user_loader
def loadUser(userId):
    userRecord = fetchUserById(userId)
    if userRecord:
        user = UserMixin()
        user.id = userRecord.user_id
        user.username = userRecord.username
        user.password = userRecord.password
        return user
    return None


@app.route("/logout")
def logout():
    logout_user()
    flash("You have been logged out", "info")
    return redirect(url_for("home"))


@login_manager.unauthorized_handler
def unauthorized():
    flash("You must be logged in to access this page.", "error")
    return redirect(url_for("login"))


@app.route("/trip/<int:tripId>")
def trip(tripId):
    dataRow = fetchTripAndCityDataByTripId(tripId)
    dataDict = {}
    dataDict["date_from"] = dataRow.date_from
    dataDict["date_to"] = dataRow.date_to
    dataDict["from_name"] = dataRow.from_name
    dataDict["to_name"] = dataRow.to_name
    dataDict["to_image"] = dataRow.to_image

    sights = getCitySights(dataDict["to_name"])

    fromAirports = fetchAirportsByCityId(dataRow.from_id)
    fromAirports = [{"code": airport[0], "name": airport[1]} for airport in fromAirports]

    toAirports = fetchAirportsByCityId(dataRow.to_id)
    toAirports = [{"code": airport[0], "name": airport[1]} for airport in toAirports]

    return render_template("trip-details.html", trip_data=dataDict, \
                           sights=sights, fromAirports=fromAirports, \
                           toAirports=toAirports)


@app.route("/get_city_predictions", methods=["POST"])
def getPredictions():
    searchQuery = request.form.get("searchQuery")
    predictions = getCityPredictions(searchQuery=searchQuery)

    return jsonify({"predictions": predictions})


@app.route("/create-trip")
def createTrip():
    departureCity = str(request.args.get("departureCity")).split(",")[0]
    destinationCity = str(request.args.get("destinationCity")).split(",")[0]
    dateFrom = str(request.args.get("dateFrom"))
    dateTo = str(request.args.get("dateTo"))

    insertTripIntoDb(userId=current_user.id, departureCity=departureCity, \
                     destinationCity=destinationCity, dateFrom=dateFrom, dateTo=dateTo)
    return redirect(url_for("tripsForUser", userId=current_user.id))


@app.route("/find_plane_tickets", methods=["POST"])
def findPlaneTickets():
    requestData = request.get_json()

    cityFrom = requestData["cityFrom"]
    cityTo = requestData["cityTo"]
    dateFrom = requestData["dateFrom"]
    dateTo = requestData["dateTo"]
    curr = requestData["curr"]

    tickets = searchForTrips(cityFrom, cityTo, dateFrom, dateTo, curr)

    return jsonify(tickets)


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
