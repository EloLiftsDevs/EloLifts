import os
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError

#josiah
from dotenv import load_dotenv
load_dotenv()
#josiah

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "DATABASE_URL", "sqlite:///elolifts.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class LiftLog(db.Model):
    __tablename__ = "lift_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False, index=True)
    exercise = db.Column(db.String(80), nullable=False)
    weight = db.Column(db.Numeric(8, 2), nullable=False)
    reps = db.Column(db.Integer, nullable=False)
    performed_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )


@app.route("/")
def home():
    return ("EloLifts basic backend server is up and running! The UI is not yet connected to our backend. "
            "See README.md for info on how to test the current lift logging implementation. "
            "This should help you to get started with the frontend and SQL stuff.")


@app.route("/api/hello")
def hello():
    return jsonify(message="Hello from the backend!")


@app.route("/api/users/<int:user_id>")
def get_user(user_id):
    return jsonify(id=user_id, name="Example User")


@app.route("/api/users/<int:user_id>/lifts", methods=["GET", "POST"])
def user_lifts(user_id):
    if request.method == "GET":
        lifts = (
            LiftLog.query.filter_by(user_id=user_id)
            .order_by(LiftLog.performed_at.desc(), LiftLog.id.desc())
            .limit(100)
            .all()
        )
        return jsonify(lifts=[serialize_lift(lift) for lift in lifts])

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify(error="Request body must be a JSON object."), 400

    exercise = data.get("exercise")
    if not isinstance(exercise, str) or not exercise.strip() or len(exercise.strip()) > 80:
        return jsonify(
            error="exercise must be a non-empty string of at most 80 characters."
        ), 400

    try:
        weight = Decimal(str(data.get("weight")))
    except (InvalidOperation, TypeError, ValueError):
        return jsonify(error="weight must be a positive number."), 400
    if not weight.is_finite() or weight <= 0 or weight > Decimal("999999.99"):
        return jsonify(
            error="weight must be a positive number no greater than 999999.99."
        ), 400

    reps = data.get("reps")
    if isinstance(reps, bool) or not isinstance(reps, int) or reps <= 0:
        return jsonify(error="reps must be a positive integer."), 400

    performed_at = datetime.now(timezone.utc)
    if "performed_at" in data:
        value = data["performed_at"]
        if not isinstance(value, str):
            return jsonify(
                error="performed_at must be an ISO 8601 timestamp with a timezone."
            ), 400
        try:
            performed_at = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return jsonify(
                error="performed_at must be an ISO 8601 timestamp with a timezone."
            ), 400
        if performed_at.tzinfo is None or performed_at.utcoffset() is None:
            return jsonify(error="performed_at must include a timezone."), 400

    lift = LiftLog(
        user_id=user_id,
        exercise=exercise.strip(),
        weight=weight,
        reps=reps,
        performed_at=performed_at,
    )
    try:
        db.session.add(lift)
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        app.logger.exception("Failed to save lift log for user %s", user_id)
        return jsonify(error="Unable to save lift right now."), 500

    return jsonify(lift=serialize_lift(lift)), 201


def serialize_lift(lift):
    performed_at = lift.performed_at
    if performed_at.tzinfo is None:
        performed_at = performed_at.replace(tzinfo=timezone.utc)
    created_at = lift.created_at
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)

    return {
        "id": lift.id,
        "user_id": lift.user_id,
        "exercise": lift.exercise,
        "weight": float(lift.weight),
        "reps": lift.reps,
        "created_at": created_at.isoformat(),
    }


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
