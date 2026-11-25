# rank rules. nothing in here touches the db so it's easy to test and change
#
# your rank is based on your big 3 total = your best estimated 1RM in each of
# RANKED_EXERCISES added up. if you haven't logged one of them it counts as 0

from decimal import ROUND_HALF_UP, Decimal

# these have to match exercises.exercise_name in seed.sql
RANKED_EXERCISES = ("Back Squat", "Bench Press", "Deadlift")

# only these statuses count toward rank, pending/rejected lifts don't
COUNTED_STATUSES = ("normal", "approved")

# epley gets way too high on high rep sets, so anything over this just counts as this many reps
MAX_REPS_FOR_ESTIMATE = 10

# (rank, min big 3 total in lb), lowest to highest
RANK_THRESHOLDS = [
    ("Bronze", 0),
    ("Silver", 500),
    ("Gold", 750),
    ("Platinum", 1000),
    ("Diamond", 1250),
    ("Elite", 1500),
]


def estimate_1rm(weight_lb, reps):
    """Epley 1RM estimate rounded to 0.1 lb. 1 rep just gives back the weight."""
    weight_lb = Decimal(weight_lb)
    if reps > 1:
        reps = min(reps, MAX_REPS_FOR_ESTIMATE)
        weight_lb = weight_lb * (1 + Decimal(reps) / 30)
    return weight_lb.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)


def rank_for_total(total_lb):
    """Gets the rank for a big 3 total and how close you are to the next one (next_rank is None if you're already at the top)."""
    index = max(i for i, (_, minimum) in enumerate(RANK_THRESHOLDS) if total_lb >= minimum)
    rank, floor = RANK_THRESHOLDS[index]
    if index + 1 == len(RANK_THRESHOLDS):
        return {"rank": rank, "next_rank": None, "progress_pct": 100, "lb_to_next": 0}
    next_rank, next_floor = RANK_THRESHOLDS[index + 1]
    return {
        "rank": rank,
        "next_rank": next_rank,
        "progress_pct": int((total_lb - floor) * 100 / (next_floor - floor)),
        "lb_to_next": next_floor - total_lb,
    }