def calculate_verification_status(
    ai_score,
    is_duplicate_risk,
    satellite_status,
    ndvi_status
):
    # Duplicate claims need manual review
    if is_duplicate_risk:
        return "Needs Review"

    # Low AI confidence needs manual review
    if ai_score is not None and ai_score < 0.4:
        return "Needs Review"

    # Suspicious satellite result
    if satellite_status == "Suspicious":
        return "Needs Review"

    # Low vegetation
    if ndvi_status == "Low vegetation":
        return "Needs Review"

    # Otherwise, claim passes MVP checks
    return "Verified"