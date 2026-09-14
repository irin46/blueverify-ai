# ========================================
# BLUEVERIFY AI
# Satellite Verification
# ========================================

def check_satellite_plausibility(
    latitude: float,
    longitude: float,
    ecosystem_type: str
):
    """
    MVP satellite plausibility check.

    This currently performs a geographic plausibility check.
    Real Sentinel-2 NDVI verification will be added later.
    """

    ecosystem = ecosystem_type.lower().strip()

    coastal_latitude = 25 <= latitude <= 30 or 8 <= latitude <= 23

    coastal_ecosystems = [
        "mangrove",
        "salt marsh",
        "seagrass",
        "blue carbon"
    ]

    ecosystem_is_coastal = ecosystem in coastal_ecosystems

    if ecosystem_is_coastal and coastal_latitude:
        return {
            "satellite_status": "Plausible",
            "coastal_match": True,
            "satellite_explanation":
                "The submitted coordinates are geographically "
                "plausible for the selected coastal ecosystem."
        }

    elif ecosystem_is_coastal:
        return {
            "satellite_status": "Suspicious",
            "coastal_match": False,
            "satellite_explanation":
                "The submitted coordinates may not be geographically "
                "consistent with the selected coastal ecosystem."
        }

    return {
        "satellite_status": "Not Applicable",
        "coastal_match": None,
        "satellite_explanation":
            "Satellite coastal plausibility checking is not "
            "required for this ecosystem type."
    }