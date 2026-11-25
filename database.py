
from datetime import datetime
from decimal import Decimal

from sqlalchemy.orm import contains_eager

from models import db, User, Exercise, LiftLog, Workout, WorkoutExercise, ComparisonGroup
from ranking import COUNTED_STATUSES, RANKED_EXERCISES, estimate_1rm, rank_for_total


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


# leaderboard - every user's rank and big 3 total, highest first
# rank is based on total so sorting by total sorts by rank too
# ties get the same spot (1, 2, 2, 4)
def get_leaderboard():
    users = User.query.all()
    bests = get_big3_bests([user.user_id for user in users])

    rows = []
    for user in users:
        total = sum(bests[user.user_id].values())
        rows.append({
            "user_id": user.user_id,
            "username": user.username,
            "rank": rank_for_total(total)["rank"],
            "total": total,
        })

    rows.sort(key=lambda row: row["total"], reverse=True)
    for i, row in enumerate(rows):
        if i > 0 and row["total"] == rows[i - 1]["total"]:
            row["position"] = rows[i - 1]["position"]
        else:
            row["position"] = i + 1

    return rows


# best estimated 1RM for each ranked lift, per user -> {user_id: {exercise_name: lb}}
# lifts they haven't logged are just 0. does everyone in one query so the leaderboard isn't slow
def get_big3_bests(user_ids):
    bests = {user_id: {name: Decimal(0) for name in RANKED_EXERCISES} for user_id in user_ids}

    lifts = (
        LiftLog.query.join(LiftLog.exercise)
        .options(contains_eager(LiftLog.exercise))
        .filter(
            LiftLog.user_id.in_(user_ids),
            Exercise.exercise_name.in_(RANKED_EXERCISES),
            LiftLog.review_status.in_(COUNTED_STATUSES),
            LiftLog.weight_lb.isnot(None),
            LiftLog.reps.isnot(None),
        )
    )
    for lift in lifts:
        user_bests = bests[lift.user_id]
        name = lift.exercise.exercise_name
        user_bests[name] = max(user_bests[name], estimate_1rm(lift.weight_lb, lift.reps))

    return bests


# all the rank info the dashboard and profile pages need
def get_rank_summary(user_id):
    bests = get_big3_bests([user_id])[user_id]
    total = sum(bests.values())

    summary = rank_for_total(total)
    summary["total"] = total
    summary["by_exercise"] = [{"exercise_name": name, "best_lb": best} for name, best in bests.items()]
    summary["position"] = next(row["position"] for row in get_leaderboard() if row["user_id"] == user_id)
    return summary


# recalculates a user's rank from their lifts and saves it to users.rank
# call this any time the lifts that count change (new lift, lift gets approved/rejected, etc)
def refresh_user_rank(user_id):
    total = sum(get_big3_bests([user_id])[user_id].values())
    return update_user_rank(user_id, rank_for_total(total)["rank"])


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


# Get a user's best lift (goes by estimated 1RM, so 135x10 beats 140x1)
def get_best_lift(user_id, exercise_id):
    lifts = LiftLog.query.filter_by(
        user_id=user_id,
        exercise_id=exercise_id
    ).all()

    best_lift = None
    best_estimate = None

    for lift in lifts:
        if lift.review_status in COUNTED_STATUSES:
            if lift.weight_lb is not None and lift.reps is not None:
                estimate = estimate_1rm(lift.weight_lb, lift.reps)
                if best_lift is None or estimate > best_estimate:
                    best_lift = lift
                    best_estimate = estimate

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

    # approving/rejecting changes whether the lift counts toward rank, so redo it
    refresh_user_rank(lift.user_id)
    return lift
