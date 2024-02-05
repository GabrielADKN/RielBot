from ai import search_ia_google
from flask import (Blueprint, request, g, jsonify)
from functions import do_login
from models import Message, User, db, Answer
from translate import translator

api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.route("/rielbot", methods=["POST"])
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

                response_data = search_ia_google(msg_eng)

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
