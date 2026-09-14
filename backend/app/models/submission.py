from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, Date, DateTime, Float, Integer, String

from app.database import Base


class Submission(Base):
    """
    Maps to the 'submissions' table in SQLite.
    Each attribute is one column in the table.
    """

    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, index=True)

    # Who submitted it
    submitter_name = Column(String, nullable=False)
    org_name = Column(String, nullable=False)

    # Where the restoration is happening
    location_name = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)

    # What kind of restoration
    ecosystem_type = Column(String, nullable=False)  # e.g. mangrove, seagrass
    area_hectares = Column(Float, nullable=False)
    start_date = Column(Date, nullable=False)

    # Supporting evidence (free text or a URL)
    evidence_text = Column(String, nullable=True)

    # Duplicate detection — set by the duplicate checker before saving
    is_duplicate_risk = Column(Boolean, default=False, nullable=False)
    # ID of the existing nearby submission, or None if not a duplicate
    duplicate_of_id = Column(Integer, nullable=True)

    # AI verification — populated by ai_analyzer.analyze_submission()
    # All nullable: if AI analysis fails the submission still saves cleanly
    ai_score = Column(Float, nullable=True)
    ai_risk_level = Column(String, nullable=True)
    ai_explanation = Column(String, nullable=True)

     # Satellite verification
    satellite_status = Column(String, nullable=True)
    coastal_match = Column(Boolean, nullable=True)
    satellite_explanation = Column(String, nullable=True)
    
    ndvi = Column(Float, nullable=True)
    ndvi_status = Column(String, nullable=True)
    ndvi_explanation = Column(String, nullable=True)

    estimated_carbon_tco2e = Column(Float, nullable=True)

    credits_released = Column(Float, nullable=True)
    credit_stage = Column(String, nullable=True)
    # Admin verification status
    # New claims start as Pending until an admin reviews them
    verification_status = Column(
        String,
        default="Pending",
        nullable=False,
    )
    # Auto-set to the moment the record is saved
    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
