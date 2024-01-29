from flask import Flask, render_template, flash, redirect
from database import SignupForm, insertUserIntoDb, LoginForm, fetchUserByUsername
from flask_bcrypt import generate_password_hash, check_password_hash, bcrypt


app = Flask(__name__)
app.config['SECRET_KEY'] = 'development_mock_secret_key'

@app.route("/")
def sayHello():
  return render_template("home.html")


@app.route("/trips")
def trips():
  return "trips"


@app.route("/signup", methods=["GET", "POST"])
def signup():
  form = SignupForm()
  if form.validate_on_submit():
    plainPassword = form.password.data
    pwhash = bcrypt.hashpw(plainPassword.encode('utf8'), bcrypt.gensalt())
    
    hashedPassword = pwhash.decode()
    
    insertedId = insertUserIntoDb(form.username.data, hashedPassword)
    flash(f"User successfully registered with ID: {insertedId}", "success")
    return redirect(f"trips/{insertedId}")
  else: 
    print(form.errors)
  return render_template("signup.html", form=form)

@app.route("/trips/<int:userId>")
def tripsForUser(userId):
  return f"TODO for id {userId}"


@app.route("/login", methods=["GET", "POST"])
def login():
  form = LoginForm()
  if form.validate_on_submit():
    inputUsername = form.username.data
    inputPassword = form.password.data
    userRecord = fetchUserByUsername(form.username.data)
    if not userRecord:
      flash("Invalid username", "error")
      return render_template("login.html", form=form)
      
    if not check_password_hash(userRecord.password, inputPassword):
      flash("Invalid password", "error")
      return render_template("login.html", form=form)
      
    flash(f"Welcome back, {userRecord.username}", "success")
    return redirect(f"trips/{userRecord.user_id}")
    
  return render_template("login.html", form=form)

if __name__ == "__main__":
  app.run(host='0.0.0.0', debug=True)
