from flask import Flask, render_template, flash, redirect
from database import SignupForm, insertUserIntoDb
from flask_bcrypt import generate_password_hash


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
    hashedPassword = str(generate_password_hash(form.password.data))
    
    insertedId = insertUserIntoDb(form.username.data, hashedPassword)
    flash(f"User successfully registered with ID: {insertedId}", "success")
    return redirect(f"trips/{insertedId}")
  else: 
    print(form.errors)
  return render_template("signup.html", form=form)

@app.route("/trips/<int:userId>")
def tripsForUser(userId):
  return f"TODO for id {userId}"


@app.route("/login")
def login():
  return "TODO"

if __name__ == "__main__":
  app.run(host='0.0.0.0', debug=True)
