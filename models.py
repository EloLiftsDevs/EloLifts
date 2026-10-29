from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Identity, false, func

db = SQLAlchemy()


# These models mirror the tables in schema.sql.
# The tables are created by running schema.sql against the database, not by the app.

class User(db.Model):
    __tablename__ = "users"

    user_id = db.Column(db.Integer, Identity(always=True), primary_key=True)
    username = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password_hash = db.Column(db.Text)
    role = db.Column(db.String(20), server_default="user")
    rank = db.Column(db.String(20), server_default="Bronze")


class Exercise(db.Model):
    __tablename__ = "exercises"

    exercise_id = db.Column(db.Integer, Identity(always=True), primary_key=True)
    exercise_name = db.Column(db.String(100), unique=True)


class LiftLog(db.Model):
    __tablename__ = "lift_logs"

    log_id = db.Column(db.Integer, Identity(always=True), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"))
    exercise_id = db.Column(db.Integer, db.ForeignKey("exercises.exercise_id"))
    weight_lb = db.Column(db.Numeric)
    reps = db.Column(db.Integer)
    # Plain TIMESTAMP (no timezone) in the schema, so the app always stores UTC.
    logged_at = db.Column(db.DateTime, server_default=func.current_timestamp())

    exercise = db.relationship("Exercise")


class Workout(db.Model):
    __tablename__ = "workouts"

    id = db.Column(db.Integer, Identity(always=True), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"))
    name = db.Column(db.String(100))
    completed = db.Column(db.Boolean, server_default=false())


class WorkoutExercise(db.Model):
    __tablename__ = "workout_exercises"

    id = db.Column(db.Integer, Identity(always=True), primary_key=True)
    workout_id = db.Column(db.Integer, db.ForeignKey("workouts.id"))
    exercise_id = db.Column(db.Integer, db.ForeignKey("exercises.exercise_id"))
    sets = db.Column(db.Integer)
    reps = db.Column(db.Integer)
    weight = db.Column(db.Integer)