import os
import pdb
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    jsonify,
    make_response,
    session,
    g,
)
from flask_debugtoolbar import DebugToolbarExtension
from forms import RegisterForm, LoginForm, MessageForm, EditUserForm
from ai import recherche_ia_google
from bing_data import get_bing_link, other_questions
from models import db, connect_db, User, Message, Answer, FunFact
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timezone
from flask_bcrypt import Bcrypt
from translate import translator
import pytz

CURR_USER_KEY = "curr_user"

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL", "postgresql:///chatbot"
)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = False
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = True
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "it's a secret")

connect_db(app)

debug = DebugToolbarExtension(app)

bcrypt = Bcrypt()


@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    add_day_fun_fact_to_g()
    if CURR_USER_KEY in session and session[CURR_USER_KEY] is not None:
        g.user = User.query.get(session[CURR_USER_KEY])
    else:
        g.user = None


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


def add_day_fun_fact_to_g():
    """Get a fun fact of the day"""
    last_fun_fact = FunFact.query.order_by(FunFact.id.desc()).first()

    eastern = pytz.timezone("America/New_York")
    today_in_eastern = datetime.now(eastern).date()

    if (
        not last_fun_fact
        or last_fun_fact.timestamp.astimezone(eastern).date() != today_in_eastern
    ):
        new_fun_fact = recherche_ia_google("give me one funfact about agriculture")

        new_fun_fact = FunFact(text=new_fun_fact)
        db.session.add(new_fun_fact)
        db.session.commit()

        last_fun_fact = new_fun_fact

    g.fun_fact = last_fun_fact


@app.route("/signup", methods=["GET", "POST"])
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


@app.route("/login", methods=["GET", "POST"])
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


@app.route("/logout")
def logout():
    """Handle logout of user."""

    session.pop(CURR_USER_KEY)
    flash("You have been logged out.", "success")
    return redirect("/login")


@app.route("/")
def home():
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/signup")
    return redirect("/chatbot")


@app.route("/chatbot", methods=["GET", "POST"])
def bot():
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/signup")

    if request.method == "POST":
        msg = request.form.get("msg", "")
        selected_language = request.form.get("language_data", "en")
        switch_value = request.form.get("advanced_mode", "false")
        # pdb.set_trace()

        # Process the message with AI, Bing, and other responses
        msg_eng = translator(text=msg, src="auto", dest="en")

        if switch_value == "true":
            ai_response = recherche_ia_google(msg_eng)
            bing_response = get_bing_link(msg_eng)
            other_response = other_questions(msg_eng)
            response_data = ai_response + bing_response + other_response
        else:
            response_data = recherche_ia_google(msg_eng)

        # Translate the response if necessary
        if selected_language != "en":
            response_data = translator(
                text=response_data, src="auto", dest=selected_language
            )

        # Save the user's message and the response to the database
        message = Message(text=msg, user_id=g.user.id)
        db.session.add(message)
        db.session.commit()

        answer = Answer(text=response_data, message_id=message.id)
        db.session.add(answer)
        db.session.commit()

        # Return the response data to be handled by the frontend
        return response_data

    # Render the chatbot page
    return render_template("chatbot.html")


@app.route("/users/<int:user_id>", methods=["GET", "POST"])
def users_show(user_id):
    """Show user profile."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/signup")

    user = User.query.get_or_404(user_id)
    form = EditUserForm(obj=user)

    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.img_url = form.img_url.data
        if form.password.data:
            hashed_password = bcrypt.generate_password_hash(form.password.data)
            user.password = hashed_password.decode("utf-8")

        db.session.commit()
        return redirect(f"/users/{user.id}")

    return render_template("users/show.html", form=form)


@app.route("/users/<int:user_id>/delete", methods=["GET", "POST"])
def delete_user(user_id):
    """Delete user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/signup")

    if request.method == "POST":
        # Handle the confirmation pop-up
        confirmation = request.form.get("confirmation")
        if confirmation == "yes":
            do_logout()
            db.session.delete(g.user)
            db.session.commit()
            flash("User deleted successfully.", "success")
            return redirect("/signup")
        else:
            flash("Deletion cancelled.", "info")
            return redirect(f"/users/{user_id}")

    return render_template("users/confirmation.html", user_id=user_id)


@app.route("/api/rielbot", methods=["POST"])
def api_login():
    """Handle user login."""
    data = request.json

    if "username" in data and "password" in data:
        username = data.get("username", "")
        password = data.get("password", "")
        msg = data.get("message", "")
        language = data.get("language", "en")

        user = User.authenticate(username, password)

        if user:
            do_login(user)
            if msg != "":
                # Process the message with AI, Bing, and other responses
                msg_eng = translator(text=msg, src="auto", dest="en")

                response_data = recherche_ia_google(msg_eng)

                # Translate the response if necessary
                if language != "en":
                    response_data = translator(
                        text=response_data, src="auto", dest=language
                    )

                # Save the user's message and the response to the database
                message = Message(text=msg, user_id=g.user.id)
                db.session.add(message)
                db.session.commit()

                answer = Answer(text=response_data, message_id=message.id)
                db.session.add(answer)
                db.session.commit()

                # Return the response data to be handled by the frontend
                return jsonify({"status": "success", "message": response_data})
            else:
                return jsonify(
                    {
                        "status": "success",
                        "message": "Logged in successfully, but no message was sent",
                    }
                )
        else:
            return jsonify(
                {"status": "error", "message": "Invalid username or password"}
            )
    else:
        return jsonify(
            {"status": "error", "message": "Username and password are required"}
        )
