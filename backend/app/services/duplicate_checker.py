import math
from typing import Optional

from sqlalchemy.orm import Session

from app.config import settings
from app.models.submission import Submission


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Return the great-circle distance in kilometres between two points
    on the Earth given their latitude and longitude in decimal degrees.

    How it works (plain English):
      1. Convert degrees to radians (math works in radians).
      2. Find the differences in lat and lon between the two points.
      3. Apply the Haversine formula — a standard way to measure curved
         distances on a sphere without needing complex calculus.
      4. Multiply by Earth's radius (6,371 km) to get the real distance.
    """
    R = 6_371  # Earth's mean radius in km

    # Convert decimal degrees → radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))

    return R * c


def find_nearby_submission(
    lat: float,
    lon: float,
    db: Session,
    radius_km: float = None,
) -> Optional[Submission]:
    """
    Query all existing submissions and return the first one whose coordinates
    are within `radius_km` of the given point.

    Returns None if no nearby submission is found.

    Why load all rows instead of using SQL distance filtering?
    - At internship/demo scale (hundreds of rows) this is perfectly fast.
    - It avoids needing PostGIS or custom SQLite extensions.
    - The Haversine calculation is done in plain Python — easy to read and test.
    """
    if radius_km is None:
        radius_km = settings.duplicate_radius_km

    existing = db.query(Submission).all()

    for submission in existing:
        distance = haversine_km(lat, lon, submission.latitude, submission.longitude)
        if distance <= radius_km:
            return submission  # first match is enough

    return None
