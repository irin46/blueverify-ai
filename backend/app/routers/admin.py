from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.orm import Session

from app.database import get_db

from app.models.submission import Submission

from app.schemas.submission import SubmissionResponse


router = APIRouter(
    prefix="/api/admin",
    tags=["Admin"]
)


# ==========================================
# GET ALL SUBMISSIONS
# ==========================================

@router.get(
    "/submissions",
    response_model=list[SubmissionResponse]
)
def get_all_submissions(
    db: Session = Depends(get_db)
):

    submissions = (
        db.query(Submission)
        .order_by(Submission.created_at.desc())
        .all()
    )

    return submissions


# ==========================================
# UPDATE CLAIM VERIFICATION STATUS
# ==========================================

@router.put(
    "/submissions/{submission_id}/status",
    response_model=SubmissionResponse
)
def update_submission_status(
    submission_id: int,
    status: str,
    db: Session = Depends(get_db)
):

    # Find the claim
    submission = (
        db.query(Submission)
        .filter(Submission.id == submission_id)
        .first()
    )

    if not submission:
        raise HTTPException(
            status_code=404,
            detail="Submission not found."
        )


    # Allowed admin statuses
    allowed_statuses = {
        "Pending",
        "Verified",
        "Needs Review"
    }


    if status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid status. "
                "Use Pending, Verified, or Needs Review."
            )
        )


    # Update status
    submission.verification_status = status

    db.commit()

    db.refresh(submission)

    return submission
