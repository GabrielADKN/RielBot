from datetime import datetime
from ai import search_ia_google
from flask import session, g
from models import FunFact, db, User
import pytz

CURR_USER_KEY = "curr_user"

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
        new_fun_fact = search_ia_google("give me one fun fact about agriculture")

        new_fun_fact = FunFact(text=new_fun_fact)
        db.session.add(new_fun_fact)
        db.session.commit()

        last_fun_fact = new_fun_fact

    g.fun_fact = last_fun_fact
