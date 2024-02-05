from flask import (Blueprint, render_template, request, redirect, flash, g,)
from forms import EditUserForm
from functions import do_logout
from models import db, User
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

users_bp = Blueprint('users', __name__, url_prefix='/users', template_folder='templates')

@users_bp.before_request
def authorize_request():
    """If we're not logged in, flash a message and redirect."""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/signup")

@users_bp.route("/<int:user_id>", methods=["GET", "POST"])
def users_show(user_id):
    """Show user profile."""

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


@users_bp.route("/<int:user_id>/delete", methods=["GET", "POST"])
def delete_user(user_id):
    """Delete user."""

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
