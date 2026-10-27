#Elo Lifts frontend pages (Sprint 1, basic version)

#Placeholder data
#Field names follow tables in schema.sql (users, exercises, lift_logs) so can be replaced with real data later

from flask import Blueprint, redirect, render_template, request, url_for

bp = Blueprint("frontend", __name__, template_folder="templates")

# users table: user_id, username, email, role, rank
FAKE_USER = {"user_id": 1, "username": "demo_lifter", "email": "demo@example.com",
             "role": "user", "rank": "Gold II"}

# exercises table: exercise_id, exercise_name
FAKE_EXERCISES = [
    {"exercise_id": 1, "exercise_name": "Back Squat"},
    {"exercise_id": 2, "exercise_name": "Bench Press"},
    {"exercise_id": 3, "exercise_name": "Deadlift"},
    {"exercise_id": 4, "exercise_name": "Overhead Press"},
    {"exercise_id": 5, "exercise_name": "Barbell Row"},
]

# not in the schema yet and by the rank system later
FAKE_RANK = {
    "next_rank": "Gold III", "progress_pct": 68, "position": 14,
    "by_exercise": [
        {"exercise_name": "Back Squat", "rank": "Gold II", "best_lb": 275},
        {"exercise_name": "Bench Press", "rank": "Silver II", "best_lb": 185},
        {"exercise_name": "Deadlift", "rank": "Gold I", "best_lb": 315},
    ],
}

# lift_logs joined with exercises: exercise_name, weight_lb, reps, logged_at
FAKE_RECENT_LIFTS = [
    {"logged_at": "Oct 12", "exercise_name": "Back Squat", "weight_lb": 255, "reps": 3},
    {"logged_at": "Oct 12", "exercise_name": "Bench Press", "weight_lb": 155, "reps": 6},
    {"logged_at": "Oct 10", "exercise_name": "Deadlift", "weight_lb": 275, "reps": 5},
]

FAKE_LEADERBOARD = [
    {"position": 1, "username": "jgarcia_lifts", "rank": "Elite III", "best_lb": 315},
    {"position": 2, "username": "carsonc", "rank": "Elite I", "best_lb": 295},
    {"position": 3, "username": "maya.presses", "rank": "Diamond II", "best_lb": 285},
    {"position": 4, "username": "josiah_w", "rank": "Platinum III", "best_lb": 255},
    {"position": 14, "username": "demo_lifter", "rank": "Silver II", "best_lb": 185},
]


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
    return render_template("frontend/dashboard.html", user=FAKE_USER,
                           rank=FAKE_RANK, lifts=FAKE_RECENT_LIFTS)


@bp.route("/log", methods=["GET", "POST"])
def log_lift():
    message = None
    if request.method == "POST":
        # Form sends exercise_id, weight_lb and reps (matching lift_logs)
        # backend hookup - save the lift here, then redirect to the dashboard
        message = "Saving lifts isn't connected to the backend yet."
    return render_template("frontend/log_lift.html", exercises=FAKE_EXERCISES, message=message)


@bp.route("/leaderboard")
def leaderboard():
    return render_template("frontend/leaderboard.html", rows=FAKE_LEADERBOARD, user=FAKE_USER)


@bp.route("/profile")
def profile():
    return render_template("frontend/profile.html", user=FAKE_USER, rank=FAKE_RANK)
