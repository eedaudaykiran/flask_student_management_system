from flask import Flask, render_template, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy

from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import os


app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# ---------------- LOGIN MANAGER ----------------

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


# ---------------- USER MODEL ----------------

class User(UserMixin, db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200))


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ---------------- STUDENT MODEL ----------------

class Student(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    age = db.Column(db.Integer)
    course = db.Column(db.String(100))


# ---------------- DEFAULT PAGE ----------------

@app.route("/")
def home():
    return redirect("/login")


# ---------------- REGISTER ----------------

@app.route("/register", methods=["GET","POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        existing_user = User.query.filter_by(username=username).first()

        if existing_user:
            flash("Username already exists", "danger")
            return redirect("/register")

        hashed_password = generate_password_hash(password)

        user = User(username=username, password=hashed_password)

        db.session.add(user)
        db.session.commit()

        flash("Registration successful! Please login.", "success")

        return redirect("/login")

    return render_template("register.html")


# ---------------- LOGIN ----------------

@app.route("/login", methods=["GET","POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):

            login_user(user)

            return redirect("/dashboard")

        flash("Invalid username or password", "danger")

    return render_template("login.html")


# ---------------- LOGOUT ----------------

@app.route("/logout")
@login_required
def logout():

    logout_user()

    return redirect("/login")


# ---------------- DASHBOARD ----------------

@app.route("/dashboard")
@login_required
def index():

    students = Student.query.all()

    return render_template("index.html", students=students)


# ---------------- ADD STUDENT ----------------

@app.route("/add", methods=["GET","POST"])
@login_required
def add_student():

    if request.method == "POST":

        name = request.form["name"]
        age = request.form["age"]
        course = request.form["course"]

        new_student = Student(name=name, age=age, course=course)

        db.session.add(new_student)
        db.session.commit()

        return redirect("/dashboard")

    return render_template("add_student.html")


# ---------------- DELETE STUDENT ----------------

@app.route("/delete/<int:id>")
@login_required
def delete_student(id):

    student = Student.query.get_or_404(id)

    db.session.delete(student)
    db.session.commit()

    return redirect("/dashboard")


# ---------------- UPDATE STUDENT ----------------

@app.route("/update/<int:id>", methods=["GET","POST"])
@login_required
def update_student(id):

    student = Student.query.get_or_404(id)

    if request.method == "POST":

        student.name = request.form["name"]
        student.age = request.form["age"]
        student.course = request.form["course"]

        db.session.commit()

        return redirect("/dashboard")

    return render_template("update_student.html", student=student)


# ---------------- RUN APP ----------------

if __name__ == "__main__":

    with app.app_context():
        db.create_all()

    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)