from flask import Flask, render_template, flash, redirect, url_for
from database import SignupForm, insertUserIntoDb, LoginForm, fetchUserByUsername, fetchUserById, fetchTripsDataByUserId
from flask_bcrypt import check_password_hash, bcrypt
from flask_login import UserMixin, login_user, logout_user, LoginManager, login_required, current_user


app = Flask(__name__)
app.config['SECRET_KEY'] = 'development_mock_secret_key'
login_manager = LoginManager(app)

@app.route("/")
def home():
  if current_user.is_authenticated:
    logout_user()
    flash("You have been logged out", "info")
  return render_template("home.html")


@app.route("/trips")
def trips():
  return "trips"


@app.route("/signup", methods=["GET", "POST"])
def signup():
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
  if current_user.id != userId:
    return redirect(url_for("logout"))
    
  tripsRecords = fetchTripsDataByUserId(userId)
  tripsListOfDicts = []
  for trip in tripsRecords:
    tempDict = {}
    tempDict["trip_id"] = trip.trip_id
    tempDict["date_from"] = trip.date_from
    tempDict["date_to"] = trip.date_to
    tempDict["city_name"] = trip.city_name
    tempDict["city_image_url"] = trip.city_image_url
    
    tripsListOfDicts.append(tempDict)
    
  return render_template("trips.html", trips=tripsListOfDicts)


@app.route("/login", methods=["GET", "POST"])
def login():
  if current_user.is_authenticated:
    logout_user()
    flash("You have been logged out", "info")
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
  return redirect(url_for("login"))


@login_manager.unauthorized_handler
def unauthorized():
    flash("You must be logged in to access this page.", "error")
    return redirect(url_for("login"))

@app.route("/trip/<int:tripId>")
def trip(tripId):
  return "TODO"


if __name__ == "__main__":
  app.run(host='0.0.0.0', debug=True)
