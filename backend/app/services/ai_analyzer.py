"""
ai_analyzer.py — BlueVerify AI verification service

PUBLIC INTERFACE
----------------
    analyze_submission(...) -> dict

The router calls analyze_submission() and receives a dict with three keys:
    ai_score        float       0.0 – 1.0
    ai_risk_level   str         "Low" | "Medium" | "High"
    ai_explanation  str         one or two sentences

CURRENT IMPLEMENTATION: deterministic heuristic rules (no external API needed).
HOW TO REPLACE THE AI PROVIDER LATER
--------------------------------------
Only the _score_submission() function below needs to change.
Everything else — the public interface, the fallback handler, the schema —
stays exactly the same whether the backend is rules, Ollama, or watsonx.ai.
"""

from datetime import date, datetime, timezone
from typing import Optional


# ---------------------------------------------------------------------------
# Known valid ecosystem types (lowercase for case-insensitive comparison)
# ---------------------------------------------------------------------------
_VALID_ECOSYSTEMS = {"mangrove", "seagrass", "saltmarsh", "kelp", "coral"}

# Maximum plausible restoration area per ecosystem type (hectares).
# Based on published blue carbon project literature.
_AREA_LIMITS = {
    "mangrove": 50_000,
    "seagrass": 100_000,
    "saltmarsh": 20_000,
    "kelp": 80_000,
    "coral": 10_000,
}

# Very rough coastal bounding boxes [lat_min, lat_max, lon_min, lon_max].
# A point that falls inside NONE of these boxes is flagged as likely inland.
# This is intentionally coarse — it avoids false positives on edge coastlines
# while still catching obviously wrong coordinates (e.g. middle of a continent).
_COASTAL_BOXES = [
    # South/Southeast Asia coasts
    (-10, 30, 60, 145),
    # Sub-Saharan Africa coasts
    (-35, 15, 8, 52),
    # West Africa
    (-5, 15, -20, 10),
    # Americas — Atlantic and Gulf coasts
    (5, 50, -100, -50),
    # Americas — Pacific coast
    (-55, 30, -130, -65),
    # Australia and Pacific
    (-45, 20, 110, 180),
    # Caribbean
    (8, 28, -90, -58),
    # Mediterranean / Red Sea
    (10, 48, -6, 43),
    # Northern Europe coasts
    (45, 72, -12, 30),
]


def _is_likely_inland(lat: float, lon: float) -> bool:
    """
    Return True if the coordinates fall outside every known coastal bounding box.
    This is a coarse sanity check, not a precise geographic test.
    """
    for lat_min, lat_max, lon_min, lon_max in _COASTAL_BOXES:
        if lat_min <= lat <= lat_max and lon_min <= lon <= lon_max:
            return False  # inside at least one coastal region — probably fine
    return True  # outside all boxes — flag as likely inland


def _score_submission(
    ecosystem_type: str,
    latitude: float,
    longitude: float,
    area_hectares: float,
    evidence_text: Optional[str],
    start_date: date,
    is_duplicate_risk: bool,
) -> tuple[float, list[str]]:
    """
    Apply heuristic rules and return (raw_score, list_of_reason_strings).

    Each rule either adds or subtracts from the base score of 0.6.
    The reasons list is used to build the human-readable explanation.

    TO REPLACE WITH REAL AI: delete this function body and replace with
    an HTTP call to your chosen provider. Keep the same return signature.
    """
    score = 0.6
    reasons: list[str] = []

    # ------------------------------------------------------------------ #
    # 1. ECOSYSTEM TYPE PLAUSIBILITY                                      #
    # ------------------------------------------------------------------ #
    eco = ecosystem_type.strip().lower()
    if eco not in _VALID_ECOSYSTEMS:
        score -= 0.2
        reasons.append(f"unrecognised ecosystem type '{ecosystem_type}'")

    # ------------------------------------------------------------------ #
    # 2. GEOGRAPHIC PLAUSIBILITY                                          #
    # ------------------------------------------------------------------ #
    if _is_likely_inland(latitude, longitude):
        score -= 0.2
        reasons.append("coordinates appear to be inland rather than coastal")

    # ------------------------------------------------------------------ #
    # 3. AREA PLAUSIBILITY                                                #
    # ------------------------------------------------------------------ #
    if area_hectares <= 0:
        score -= 0.3
        reasons.append("area must be greater than zero")
    else:
        limit = _AREA_LIMITS.get(eco)  # None if ecosystem was already unknown
        if limit is not None and area_hectares > limit:
            score -= 0.2
            reasons.append(
                f"claimed area of {area_hectares:,.0f} ha exceeds the plausible"
                f" maximum of {limit:,} ha for {eco} ecosystems"
            )

    # ------------------------------------------------------------------ #
    # 4. EVIDENCE QUALITY                                                 #
    # ------------------------------------------------------------------ #
    evidence = (evidence_text or "").strip()
    if not evidence:
        score -= 0.15
        reasons.append("no supporting evidence was provided")
    elif len(evidence) < 20:
        score -= 0.10
        reasons.append("evidence text is too brief to be meaningful")
    elif len(evidence) >= 50:
        score += 0.10
        reasons.append("detailed evidence text provided")

    # ------------------------------------------------------------------ #
    # 5. TEMPORAL PLAUSIBILITY                                            #
    # ------------------------------------------------------------------ #
    today = datetime.now(timezone.utc).date()
    if start_date > today:
        score -= 0.15
        reasons.append("project start date is in the future")
    elif (today - start_date).days > 365 * 10:
        score -= 0.05
        reasons.append("project started more than 10 years ago")

    # ------------------------------------------------------------------ #
    # 6. DUPLICATE RISK                                                   #
    # ------------------------------------------------------------------ #
    if is_duplicate_risk:
        score -= 0.15
        reasons.append("a nearby submission already exists for this location")

    return score, reasons


def _derive_risk_level(score: float) -> str:
    """Map a clamped score to a risk label."""
    if score >= 0.65:
        return "Low"
    if score >= 0.40:
        return "Medium"
    return "High"


def _build_explanation(score: float, risk_level: str, reasons: list[str]) -> str:
    """
    Compose a short human-readable explanation from the triggered rules.
    Always produces at least one sentence.
    """
    if not reasons:
        return (
            f"Plausibility score: {score:.2f}. "
            "No significant concerns identified; submission appears credible."
        )

    # Separate positive and negative reasons for a more natural sentence
    positives = [r for r in reasons if r.startswith("detailed")]
    negatives = [r for r in reasons if r not in positives]

    parts: list[str] = []

    if negatives:
        concern_str = "; ".join(negatives)
        parts.append(f"Concerns: {concern_str}.")

    if positives:
        positive_str = "; ".join(positives)
        parts.append(f"Strengths: {positive_str}.")

    parts.append(f"Overall risk level: {risk_level} (score {score:.2f}).")

    return " ".join(parts)


# ---------------------------------------------------------------------------
# PUBLIC INTERFACE — the only function the router should call
# ---------------------------------------------------------------------------

def analyze_submission(
    ecosystem_type: str,
    latitude: float,
    longitude: float,
    area_hectares: float,
    evidence_text: Optional[str],
    start_date: date,
    is_duplicate_risk: bool,
) -> dict:
    """
    Analyze a blue-carbon restoration submission and return a verification result.

    Always returns a dict — never raises. If an unexpected error occurs,
    a safe fallback is returned so the submission still saves successfully.

    Returns:
        {
            "ai_score":       float | None,
            "ai_risk_level":  str,
            "ai_explanation": str,
        }
    """
    try:
        raw_score, reasons = _score_submission(
            ecosystem_type=ecosystem_type,
            latitude=latitude,
            longitude=longitude,
            area_hectares=area_hectares,
            evidence_text=evidence_text,
            start_date=start_date,
            is_duplicate_risk=is_duplicate_risk,
        )

        # Clamp score to valid range
        score = round(max(0.0, min(1.0, raw_score)), 2)
        risk_level = _derive_risk_level(score)
        explanation = _build_explanation(score, risk_level, reasons)

        return {
            "ai_score": score,
            "ai_risk_level": risk_level,
            "ai_explanation": explanation,
        }

    except Exception as exc:  # noqa: BLE001
        # Never let an analysis failure crash the submission endpoint.
        # Log the error (visible in uvicorn console) and return a safe fallback.
        print(f"[ai_analyzer] analysis failed: {exc}")
        return {
            "ai_score": None,
            "ai_risk_level": "Unknown",
            "ai_explanation": "AI analysis unavailable. Manual review required.",
        }
