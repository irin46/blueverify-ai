# ========================================
# BLUEVERIFY AI
# Carbon Estimator
# ========================================

CARBON_FACTORS = {
    "mangrove": 200.0,
    "salt marsh": 150.0,
    "seagrass": 100.0,
    "blue carbon": 150.0
}


def estimate_carbon(ecosystem_type: str, area_hectares: float):

    ecosystem = ecosystem_type.lower().strip()

    factor = CARBON_FACTORS.get(ecosystem, 100.0)

    estimated_carbon = area_hectares * factor

    return {
        "estimated_carbon_tco2e": round(estimated_carbon, 2)
    }