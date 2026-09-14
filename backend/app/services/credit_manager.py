# ========================================
# BLUEVERIFY AI
# Staged Carbon Credit Manager
# ========================================

def calculate_credit_release(
    estimated_carbon_tco2e,
    verification_status,
    credit_stage="Stage 1"
):

    if estimated_carbon_tco2e is None:
        return {
            "credits_released": 0.0,
            "credit_stage": "Not Available"
        }

    if verification_status != "Verified":
        return {
            "credits_released": 0.0,
            "credit_stage": "On Hold"
        }

    if credit_stage == "Stage 1":
        percentage = 0.20
        stage_name = "Stage 1 - Initial Release"

    elif credit_stage == "Stage 2":
        percentage = 0.50
        stage_name = "Stage 2 - Survival Verification"

    elif credit_stage == "Stage 3":
        percentage = 1.00
        stage_name = "Stage 3 - Final Release"

    else:
        percentage = 0.0
        stage_name = "On Hold"

    credits_released = estimated_carbon_tco2e * percentage

    return {
        "credits_released": round(credits_released, 2),
        "credit_stage": stage_name
    }