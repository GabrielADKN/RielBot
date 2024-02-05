from ai import search_ia_google
from bing_data import get_bing_link, other_questions
from flask import (Blueprint, render_template, request, redirect, flash, g,)

from models import db, Message, Answer
from translate import translator

chatbot_bp = Blueprint("chatbot", __name__, template_folder="templates")


@chatbot_bp.before_request
def authorize_request():
    """If we're not logged in, flash a message and redirect."""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/signup")


@chatbot_bp.route("/chatbot", methods=["GET", "POST"])
def bot():
    if request.method == "POST":
        msg = request.form.get("msg", "")
        selected_language = request.form.get("language_data", "en")
        switch_value = request.form.get("advanced_mode", "false")

        # Process the message with AI, Bing, and other responses
        msg_eng = translator(text=msg, src="auto", dest="en")

        if switch_value == "true":
            ai_response = search_ia_google(msg_eng)
            bing_response = get_bing_link(msg_eng)
            other_response = other_questions(msg_eng)
            response_data = ai_response + bing_response + other_response
        else:
            response_data = search_ia_google(msg_eng)

        # Translate the response if necessary
        if selected_language != "en":
            response_data = translator(
                text=response_data, src="auto", dest=selected_language
            )

        # Save the user's message and the response to the database
        try:
            # Create the message
            message = Message(text=msg, user_id=g.user.id)
            db.session.add(message)
            # Flush the session to get the message ID without committing the transaction
            db.session.flush()

            answer = Answer(text=response_data, message_id=message.id)
            db.session.add(answer)

            # Commit both Message and Answer in a single transaction
            db.session.commit()

        except Exception as e:
            db.session.rollback()

        return response_data

    # Render the chatbot page
    return render_template("chatbot/chatbot.html")
