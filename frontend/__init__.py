#Elo Lifts frontend pages (Sprint 1, basic version)

#Users, exercises and lifts come from the database (see models.py)
#Ranks and the leaderboard are still placeholder data until the rank system exists

from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation

from flask import Blueprint, current_app, redirect, render_template, request, url_for
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload

from models import Exercise, LiftLog, User, db

bp = Blueprint("frontend", __name__, template_folder="templates")

#No login yet, so every page acts as this user
#backend hookup - replace with the logged-in user once authentication is added
CURRENT_USER_ID = 1

# not in the schema yet and by the rank system later
FAKE_RANK = {
    "next_rank": "Gold III", "progress_pct": 68, "position": 14,
    "by_exercise": [
        {"exercise_name": "Back Squat", "rank": "Gold II", "best_lb": 275},
        {"exercise_name": "Bench Press", "rank": "Silver II", "best_lb": 185},
        {"exercise_name": "Deadlift", "rank": "Gold I", "best_lb": 315},
    ],
}

FAKE_LEADERBOARD = [
    {"position": 1, "username": "jgarcia_lifts", "rank": "Elite III", "best_lb": 315},
    {"position": 2, "username": "carsonc", "rank": "Elite I", "best_lb": 295},
    {"position": 3, "username": "maya.presses", "rank": "Diamond II", "best_lb": 285},
    {"position": 4, "username": "josiah_w", "rank": "Platinum III", "best_lb": 255},
    {"position": 14, "username": "demo_lifter", "rank": "Silver II", "best_lb": 185},
]


def get_current_user():
    return db.get_or_404(User, CURRENT_USER_ID)


@bp.route("/login", methods=["GET", "POST"])
def login():
    message = None
    if request.method == "POST":
        # backend hookup - authenticate the user here
        message = "Login isn't connected to the backend yet."
    return render_template("frontend/login.html", message=message, hide_nav=True)


@bp.route("/register", methods=["GET", "POST"])
def register():
    message = None
    if request.method == "POST":
        # backend hookup - create the user account here.
        message = "Sign-up isn't connected to the backend yet."
    return render_template("frontend/register.html", message=message, hide_nav=True)


@bp.route("/logout")
def logout():
    # backend hookup - log user out here
    return redirect(url_for("frontend.login"))


@bp.route("/dashboard")
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
                           rank=FAKE_RANK, lifts=recent_lifts)


@bp.route("/log", methods=["GET", "POST"])
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
def leaderboard():
    return render_template("frontend/leaderboard.html", rows=FAKE_LEADERBOARD, user=get_current_user())


@bp.route("/profile")
def profile():
    return render_template("frontend/profile.html", user=get_current_user(), rank=FAKE_RANK)


def save_lift(user, form):
    """Check the log-lift form and save it. Returns (error message, status), or (None, None) once saved."""
    # Form sends exercise_id, weight_lb and reps (matching lift_logs)
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
    return None, None


def format_date(logged_at):
    #logged_at is stored in UTC, so convert it to the server's local time before showing it
    local = logged_at.replace(tzinfo=timezone.utc).astimezone()
    return f"{local:%b} {local.day}"