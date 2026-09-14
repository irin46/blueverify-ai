from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.services.satellite_checker import check_satellite_plausibility
from app.database import get_db
from app.models.submission import Submission
from app.schemas.submission import SubmissionCreate, SubmissionResponse
from app.services.ai_analyzer import analyze_submission
from app.services.duplicate_checker import find_nearby_submission
from app.services.ndvi_checker import calculate_ndvi
from app.services.verification_engine import calculate_verification_status
from app.services.carbon_estimator import estimate_carbon
from app.services.credit_manager import calculate_credit_release
# APIRouter is like a mini FastAPI app — we register it in main.py
router = APIRouter(prefix="/api/submissions", tags=["Submissions"])


@router.post("", response_model=SubmissionResponse, status_code=201)
def create_submission(payload: SubmissionCreate, db: Session = Depends(get_db)):

    # 1. Duplicate check
    nearby = find_nearby_submission(
        payload.latitude,
        payload.longitude,
        db
    )

    is_dup = nearby is not None

    # 2. AI verification
    ai_result = analyze_submission(
        ecosystem_type=payload.ecosystem_type,
        latitude=payload.latitude,
        longitude=payload.longitude,
        area_hectares=payload.area_hectares,
        evidence_text=payload.evidence_text,
        start_date=payload.start_date,
        is_duplicate_risk=is_dup,
    )

    # 3. Satellite verification
    satellite_result = check_satellite_plausibility(
        latitude=payload.latitude,
        longitude=payload.longitude,
        ecosystem_type=payload.ecosystem_type,
    )

    # 4. NDVI verification
    ndvi_result = calculate_ndvi(
        latitude=payload.latitude,
        longitude=payload.longitude,
    )


     # 5. Carbon estimation
    carbon_result = estimate_carbon(
        ecosystem_type=payload.ecosystem_type,
        area_hectares=payload.area_hectares,
    )

    # 6. Combined verification
    verification_status = calculate_verification_status(
        ai_score=ai_result.get("ai_score"),
        is_duplicate_risk=is_dup,
        satellite_status=satellite_result.get("satellite_status"),
        ndvi_status=ndvi_result.get("ndvi_status"),
    )

    # 7. Staged carbon credit release
    credit_result = calculate_credit_release(
        estimated_carbon_tco2e=carbon_result.get("estimated_carbon_tco2e"),
        verification_status=verification_status,
        credit_stage="Stage 1",
    )

    # 8. Create submission
    submission = Submission(
        **payload.model_dump(),
        is_duplicate_risk=is_dup,
        duplicate_of_id=nearby.id if is_dup else None,
        **ai_result,
        **satellite_result,
        **ndvi_result,
        **carbon_result,
        **credit_result,
        verification_status=verification_status,
    )

    db.add(submission)
    db.commit()
    db.refresh(submission)

    return submission

@router.put("/{submission_id}/credit-stage")
def update_credit_stage(
    submission_id: int,
    stage: str,
    db: Session = Depends(get_db)
):

    submission = db.query(Submission).filter(
        Submission.id == submission_id
    ).first()

    if not submission:
        raise HTTPException(
            status_code=404,
            detail="Submission not found"
        )

    if submission.verification_status != "Verified":
        raise HTTPException(
            status_code=400,
            detail="Only verified submissions can release credits"
        )

    stage = stage.strip().strip('"')

    if stage not in ["Stage 1", "Stage 2", "Stage 3"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid credit stage"
        )

    credit_result = calculate_credit_release(
        estimated_carbon_tco2e=submission.estimated_carbon_tco2e,
        verification_status=submission.verification_status,
        credit_stage=stage
    )

    submission.credits_released = credit_result["credits_released"]
    submission.credit_stage = credit_result["credit_stage"]

    db.commit()
    db.refresh(submission)

    return {
        "submission_id": submission.id,
        "estimated_carbon_tco2e": submission.estimated_carbon_tco2e,
        "credits_released": submission.credits_released,
        "credit_stage": submission.credit_stage
    }

@router.get("", response_model=list[SubmissionResponse])
def get_submissions(db: Session = Depends(get_db)):
    """
    Retrieve all restoration submissions.
    """
    submissions = (
        db.query(Submission)
        .order_by(Submission.id.desc())
        .all()
    )

    return submissions
@router.get("/{submission_id}", response_model=SubmissionResponse)
def get_submission(submission_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a single submission by its id.
    Returns 404 if no submission with that id exists.
    """
    submission = db.get(Submission, submission_id)
    if submission is None:
        raise HTTPException(status_code=404, detail="Submission not found")
    return submission

@router.delete("/{submission_id}")
def delete_submission(submission_id: int, db: Session = Depends(get_db)):
    submission = db.query(Submission).filter(
        Submission.id == submission_id
    ).first()

    if not submission:
        raise HTTPException(
            status_code=404,
            detail="Submission not found"
        )

    db.delete(submission)
    db.commit()

    return {
        "message": f"Submission {submission_id} deleted successfully"
    }