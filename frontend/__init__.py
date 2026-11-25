#Elo Lifts frontend pages (Sprint 1, basic version)

#users, exercises and lifts all come from the db (models.py)
#rank = squat + bench + deadlift total, the rules are in ranking.py

import re
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from urllib.parse import urlsplit

from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import joinedload
from werkzeug.security import check_password_hash, generate_password_hash

from database import get_leaderboard, get_rank_summary, refresh_user_rank
from models import Exercise, LiftLog, User, db

bp = Blueprint("frontend", __name__, template_folder="templates")

# this gets attached to the app in app.py
login_manager = LoginManager()
login_manager.login_view = "frontend.login"  # @login_required sends you here if you're not logged in

EMAIL_TAKEN = "An account with that email already exists."


@bp.app_template_filter("lb")
def format_lb(value):
    # for showing weights in templates. {{ total|lb }} makes 1250.0 -> "1,250" and leaves 157.5 as "157.5"
    return f"{value:,.1f}".removesuffix(".0")


@login_manager.user_loader
def load_user(user_id):
    # runs every request to get the User from the session cookie
    # returning None for suspended users logs them out next time they load a page
    user = db.session.get(User, int(user_id))
    return user if user is not None and user.is_active else None


def get_current_user():
    # only used on @login_required pages so there's always a logged in user here
    return current_user


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("frontend.dashboard"))
    message = None
    status = 200
    if request.method == "POST":
        user = find_user_by_email(normalize_email(request.form.get("email")))
        password = request.form.get("password", "")
        # same error for wrong email or wrong password so nobody can use this to check which emails have accounts
        if user is None or not user.password_hash or not check_password_hash(user.password_hash, password):
            message, status = "Incorrect email or password.", 401
        elif not login_user(user, remember=request.form.get("remember") == "on"):
            message, status = "This account has been suspended.", 403
        else:
            return redirect(safe_next_url(request.args.get("next")))
    return render_template("frontend/login.html", message=message, hide_nav=True), status


@bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("frontend.dashboard"))
    message = None
    status = 200
    if request.method == "POST":
        user, message, status = create_account(request.form)
        if user is not None:
            login_user(user)
            return redirect(url_for("frontend.dashboard"))
    return render_template("frontend/register.html", message=message, hide_nav=True), status


@bp.route("/logout")
def logout():
    logout_user()
    flash("You've been logged out.")
    return redirect(url_for("frontend.login"))


@bp.route("/dashboard")
@login_required
def dashboard():
    user = get_current_user()
    lifts = (
        LiftLog.query.options(joinedload(LiftLog.exercise))
        .filter_by(user_id=user.user_id)
        .order_by(LiftLog.logged_at.desc(), LiftLog.log_id.desc())
        .limit(10)
        .all()
    )
    recent_lifts = [
        {"logged_at": format_date(lift.logged_at), "exercise_name": lift.exercise.exercise_name,
         "weight_lb": lift.weight_lb, "reps": lift.reps}
        for lift in lifts
    ]
    return render_template("frontend/dashboard.html", user=user,
                           rank=get_rank_summary(user.user_id), lifts=recent_lifts)


@bp.route("/log", methods=["GET", "POST"])
@login_required
def log_lift():
    user = get_current_user()
    message = None
    status = 200
    if request.method == "POST":
        message, status = save_lift(user, request.form)
        if message is None:
            return redirect(url_for("frontend.dashboard"))
    exercises = Exercise.query.order_by(Exercise.exercise_name).all()
    return render_template("frontend/log_lift.html", exercises=exercises, message=message), status


@bp.route("/leaderboard")
@login_required
def leaderboard():
    return render_template("frontend/leaderboard.html", rows=get_leaderboard(), user=get_current_user())


@bp.route("/profile")
@login_required
def profile():
    user = get_current_user()
    return render_template("frontend/profile.html", user=user, rank=get_rank_summary(user.user_id))


def normalize_email(email):
    # lowercase it so "Bob@x.com" and "bob@x.com" are the same account
    return (email or "").strip().lower()


def find_user_by_email(email):
    if not email:
        return None
    # lower() here too in case of old rows added by hand before we started lowercasing emails
    return User.query.filter(func.lower(User.email) == email).first()


def create_account(form):
    """Checks the sign up form and makes the user. Returns (user, None, None) or (None, error msg, status)."""
    username = form.get("username", "").strip()
    email = normalize_email(form.get("email"))
    password = form.get("password", "")

    if not 3 <= len(username) <= 30:
        return None, "Username must be 3 to 30 characters.", 400
    # users.email is VARCHAR(100)
    if len(email) > 100 or not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        return None, "Please enter a valid email address.", 400
    if len(password) < 8:
        return None, "Password must be at least 8 characters.", 400
    if find_user_by_email(email) is not None:
        return None, EMAIL_TAKEN, 409

    user = User(username=username, email=email, password_hash=generate_password_hash(password))
    try:
        db.session.add(user)
        db.session.commit()
    except IntegrityError:
        # someone else signed up with the same email in between our check and this insert (users.email is UNIQUE)
        db.session.rollback()
        return None, EMAIL_TAKEN, 409
    except SQLAlchemyError:
        db.session.rollback()
        current_app.logger.exception("Failed to create account for %s", email)
        return None, "Unable to create your account right now.", 500
    return user, None, None


def safe_next_url(target):
    """Only follow ?next= if it points to our own site, otherwise the login page could send people anywhere."""
    if target and target.startswith("/") and "\\" not in target:
        parts = urlsplit(target)
        if not parts.scheme and not parts.netloc:
            return target
    return url_for("frontend.dashboard")


def save_lift(user, form):
    """Checks the log lift form and saves it. Returns (error msg, status), or (None, None) if it worked."""
    # form field names match the lift_logs columns (exercise_id, weight_lb, reps)
    exercise_id = form.get("exercise_id", type=int)
    if exercise_id is None or db.session.get(Exercise, exercise_id) is None:
        return "Please choose an exercise from the list.", 400

    try:
        weight = Decimal(form.get("weight_lb", ""))
    except InvalidOperation:
        return "Weight must be a positive number.", 400
    if not weight.is_finite() or weight <= 0 or weight > Decimal("999999.99"):
        return "Weight must be a positive number no greater than 999999.99.", 400

    reps = form.get("reps", type=int)
    if reps is None or reps <= 0:
        return "Reps must be a positive whole number.", 400

    lift = LiftLog(
        user_id=user.user_id,
        exercise_id=exercise_id,
        weight_lb=weight,
        reps=reps,
        logged_at=datetime.now(timezone.utc).replace(tzinfo=None),
    )
    try:
        db.session.add(lift)
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        current_app.logger.exception("Failed to save lift log for user %s", user.user_id)
        return "Unable to save lift right now.", 500

    # a new PR might bump them up a rank. pages calculate rank from the lifts anyway,
    # so if this fails the lift is still saved and users.rank is just out of date
    try:
        refresh_user_rank(user.user_id)
    except SQLAlchemyError:
        db.session.rollback()
        current_app.logger.exception("Lift saved but rank update failed for user %s", user.user_id)
    return None, None


def format_date(logged_at):
    #logged_at is UTC so convert it to the server's local time for display
    local = logged_at.replace(tzinfo=timezone.utc).astimezone()
    return f"{local:%b} {local.day}"