from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user

from app.auth import auth_bp
from app.auth.forms import LoginForm
from app.models import User


@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    if current_user.is_authenticated:
        return redirect(url_for("admin.dashboard"))

    form = LoginForm()

    if form.validate_on_submit():

        user = User.query.filter_by(
            email=form.email.data
        ).first()

        if user and user.check_password(form.password.data):

            login_user(
                user,
                remember=form.remember.data
            )

            print("=" * 50)
            print("LOGIN SUCCESS")
            print("Authenticated:", current_user.is_authenticated)
            print("User ID:", current_user.get_id())
            print("=" * 50)

            flash("Welcome back!", "success")

            next_page = request.args.get("next")

            return redirect(
                next_page or url_for("admin.dashboard")
            )

        flash("Invalid email or password.", "danger")

    return render_template(
        "auth/login.html",
        form=form
    )


@auth_bp.route("/logout")
@login_required
def logout():

    logout_user()

    flash("Logged out successfully.", "success")

    return redirect(url_for("auth.login"))