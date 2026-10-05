def calculate_forgetting_risk(
    difficulty,
    quiz_score,
    days_since_study,
    revisions
):
    difficulty_factor = difficulty * 8
    score_factor = (100 - quiz_score) * 0.45
    time_factor = days_since_study * 5
    revision_factor = revisions * 7

    risk = (
        difficulty_factor
        + score_factor
        + time_factor
        - revision_factor
    )

    risk = max(0, min(100, round(risk)))

    if risk >= 75:
        level = "Critical"
    elif risk >= 50:
        level = "High"
    elif risk >= 25:
        level = "Medium"
    else:
        level = "Low"

    return risk, level