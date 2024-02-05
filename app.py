import os
from flask import Flask, redirect, flash, session, g

from functions import add_day_fun_fact_to_g
from models import connect_db, User
from blueprints.users.users import users_bp
from blueprints.chatbot.chatbot import chatbot_bp
from blueprints.api.api import api_bp
from blueprints.connection.connection import connection_bp

CURR_USER_KEY = "curr_user"

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL", "postgresql:///chatbot"
)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = False
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = True
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "it's a secret")

app.register_blueprint(users_bp)
app.register_blueprint(chatbot_bp)
app.register_blueprint(api_bp)
app.register_blueprint(connection_bp)

connect_db(app)


@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    add_day_fun_fact_to_g()
    if CURR_USER_KEY in session and session[CURR_USER_KEY] is not None:
        g.user = User.query.get(session[CURR_USER_KEY])
    else:
        g.user = None

@app.route("/")
def home():
    return redirect("/chatbot")
