from flask import (Blueprint, render_template, flash, redirect, session,)
from forms import LoginForm, RegisterForm
from functions import do_login
from models import User, db
from sqlalchemy.exc import IntegrityError

connection_bp = Blueprint("connection", __name__, template_folder="templates")

CURR_USER_KEY = "curr_user"


@connection_bp.route("/signup", methods=["GET", "POST"])
def signup():
    form = RegisterForm()

    if form.validate_on_submit():
        try:
            user = User.register(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data,
                first_name=form.first_name.data,
                last_name=form.last_name.data,
            )
            db.session.commit()

            # Flash a success message and redirect
            flash("Registration successful!", "success")
            do_login(user)
            return redirect("/chatbot")

        except IntegrityError:
            db.session.rollback()
            # Flash an error message for duplicate username
            flash("Username already taken. Please choose another.", "danger")
            return render_template("signup.html", form=form)

        except Exception as e:
            db.session.rollback()
            # Handle unexpected errors
            flash(f"An error occurred: {str(e)}", "danger")
            return render_template("signup.html", form=form)

    else:
        return render_template("signup.html", form=form)


@connection_bp.route("/login", methods=["GET", "POST"])
def login():
    """Handle user login."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data, form.password.data)

        if user:
            do_login(user)
            # flash(f"Hello, {user.username}!", "success")
            return redirect("/chatbot")

        flash("Invalid credentials.", "danger")

    return render_template("login.html", form=form)


@connection_bp.route("/logout")
def logout():
    """Handle logout of user."""

    session.pop(CURR_USER_KEY)
    flash("You have been logged out.", "success")
    return redirect("/login")
