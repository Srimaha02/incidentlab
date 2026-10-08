"""Pure scoring functions."""

HINT_COST = 25
WRONG_COST = 25
MIN_SCORE = 10


def compute_score(points, hints_used, wrong_attempts):
    return max(
        points
        - HINT_COST * hints_used
        - WRONG_COST * wrong_attempts,
        MIN_SCORE,
    )