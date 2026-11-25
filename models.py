from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Identity, false, func

db = SQLAlchemy()


# these match the tables in schema.sql
# the app doesn't make the tables, you have to run schema.sql on the db yourself

class User(UserMixin, db.Model):
    __tablename__ = "users"

    user_id = db.Column(db.Integer,  primary_key=True)
    username = db.Column(db.String(100))
    # always saved lowercase (normalize_email in frontend/__init__.py) so UNIQUE basically ignores case
    email = db.Column(db.String(100), unique=True)
    password_hash = db.Column(db.Text)
    role = db.Column(db.String(20), server_default="user")
    rank = db.Column(db.String(20), server_default="Bronze")
    suspended = db.Column(db.Boolean, default=False)

    # flask-login looks for "id" by default but our key is user_id
    def get_id(self):
        return str(self.user_id)

    # flask-login won't log in inactive users, so this is what blocks suspended accounts
    @property
    def is_active(self):
        return not self.suspended


class Exercise(db.Model):
    __tablename__ = "exercises"

    exercise_id = db.Column(db.Integer, primary_key=True)
    exercise_name = db.Column(db.String(100), unique=True)
    measurement = db.Column(db.Text, default="weight_reps")


class LiftLog(db.Model):
    __tablename__ = "lift_logs"

    log_id = db.Column(db.Integer,  primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"))
    exercise_id = db.Column(db.Integer, db.ForeignKey("exercises.exercise_id"))
    weight_lb = db.Column(db.Numeric)
    reps = db.Column(db.Integer)
    # schema uses plain TIMESTAMP (no timezone) so we always store UTC
    logged_at = db.Column(db.DateTime, server_default=func.current_timestamp())

    exercise = db.relationship("Exercise")

    sets = db.Column(db.Integer, default=1)
    review_status = db.Column(db.Text, default="normal")


class Workout(db.Model):
    __tablename__ = "workouts"

    id = db.Column(db.Integer,  primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"))
    name = db.Column(db.String(100))
    completed = db.Column(db.Boolean, server_default=false())

    completed_at = db.Column(db.DateTime)


class WorkoutExercise(db.Model):
    __tablename__ = "workout_exercises"

    id = db.Column(db.Integer,  primary_key=True)
    workout_id = db.Column(db.Integer, db.ForeignKey("workouts.id"))
    exercise_id = db.Column(db.Integer, db.ForeignKey("exercises.exercise_id"))
    sets = db.Column(db.Integer)
    reps = db.Column(db.Integer)
    weight = db.Column(db.Integer)


class ComparisonGroup(db.Model):
    __tablename__ = "comparison_groups"

    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), primary_key=True)