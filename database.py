
from datetime import datetime
from models import db, User, Exercise, LiftLog, Workout, WorkoutExercise, ComparisonGroup


# Create a workout
def create_workout(user_id, workout_name):
    workout = Workout(user_id=user_id, name=workout_name)
    db.session.add(workout)
    db.session.commit()
    return workout


# Add an exercise to a workout
def add_exercise_to_workout(workout_id, exercise_id, sets, reps, weight):
    workout_exercise = WorkoutExercise(
        workout_id=workout_id,
        exercise_id=exercise_id,
        sets=sets,
        reps=reps,
        weight=weight
    )

    db.session.add(workout_exercise)
    db.session.commit()
    return workout_exercise


# Mark a workout as completed
def complete_workout(workout_id):
    workout = db.session.get(Workout, workout_id)

    if workout is None:
        return None

    workout.completed = True
    workout.completed_at = datetime.utcnow()

    db.session.commit()
    return workout


# Get a user's workout history
def get_workout_history(user_id):
    workouts = Workout.query.filter_by(user_id=user_id).all()
    return workouts


# Get exercises in a workout
def get_workout_exercises(workout_id):
    exercises = WorkoutExercise.query.filter_by(workout_id=workout_id).all()
    return exercises


# Get completed workouts
def get_completed_workouts(user_id):
    workouts = Workout.query.filter_by(user_id=user_id, completed=True).all()
    return workouts


# Get users ordered by rank
def get_leaderboard():
    rank_order = ["Bronze", "Silver", "Gold", "Platinum", "Diamond"]
    users = User.query.all()

    users.sort(
        key=lambda user: rank_order.index(user.rank)
        if user.rank in rank_order else -1,
        reverse=True
    )

    return users


# Update a user's rank
def update_user_rank(user_id, rank):
    user = db.session.get(User, user_id)

    if user is None:
        return None

    user.rank = rank
    db.session.commit()
    return user


# Get lifts for an exercise
def get_exercise_stats(exercise_id):
    lifts = LiftLog.query.filter_by(exercise_id=exercise_id).all()
    return lifts


# Get a user's best lift
def get_best_lift(user_id, exercise_id):
    lifts = LiftLog.query.filter_by(
        user_id=user_id,
        exercise_id=exercise_id
    ).all()

    best_lift = None

    for lift in lifts:
        if lift.review_status in ("normal", "approved"):
            if lift.weight_lb is not None:
                if best_lift is None or lift.weight_lb > best_lift.weight_lb:
                    best_lift = lift

    return best_lift


# Add a comparison group member
def add_comparison_member(user_id, member_id):
    member = ComparisonGroup(user_id=user_id, member_id=member_id)
    db.session.add(member)
    db.session.commit()
    return member


# Get comparison group members
def get_comparison_group(user_id):
    members = ComparisonGroup.query.filter_by(user_id=user_id).all()
    return members


# Remove a comparison group member
def remove_comparison_member(user_id, member_id):
    member = ComparisonGroup.query.filter_by(
        user_id=user_id,
        member_id=member_id
    ).first()

    if member is None:
        return False

    db.session.delete(member)
    db.session.commit()
    return True


# Search for users by username
def search_users(username):
    users = User.query.filter(User.username.ilike(f"%{username}%")).all()
    return users


# Get lifts waiting for review
def get_flagged_lifts():
    lifts = LiftLog.query.filter_by(review_status="pending").all()
    return lifts


# Update a lift's review status
def update_lift_status(log_id, review_status):
    lift = db.session.get(LiftLog, log_id)

    if lift is None:
        return None

    lift.review_status = review_status
    db.session.commit()
    return lift
