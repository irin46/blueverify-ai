// ========================================
// BLUEVERIFY AI
// Submit Claim Page Logic
// ========================================

const API_BASE = "http://127.0.0.1:8000";

const claimForm = document.getElementById("claimForm");
const resultContainer = document.getElementById("result");


// ========================================
// FORM SUBMISSION
// ========================================

if (claimForm) {

    claimForm.addEventListener("submit", async function (event) {

        event.preventDefault();

        const submitButton = claimForm.querySelector(
            'button[type="submit"]'
        );

        const originalButtonText = submitButton
            ? submitButton.textContent
            : "Verify Claim →";


        // Disable button while checking
        if (submitButton) {
            submitButton.disabled = true;
            submitButton.textContent = "Verifying...";
        }


        // Show loading message
        if (resultContainer) {

            resultContainer.classList.add("show");

            resultContainer.innerHTML = `
                <div class="result-box">

                    <div class="result-header">

                        <div>
                            <p class="section-label">
                                BLUEVERIFY AI
                            </p>

                            <h2>
                                Analyzing claim...
                            </h2>

                            <p>
                                BlueVerify is checking your restoration claim.
                            </p>
                        </div>

                    </div>

                </div>
            `;
        }


        // ========================================
        // GET FORM DATA
        // ========================================

        const formData = new FormData(claimForm);

        const payload = {

            submitter_name:
                formData.get("submitter_name"),

            org_name:
                formData.get("org_name"),

            location_name:
                formData.get("location_name"),

            latitude:
                Number(formData.get("latitude")),

            longitude:
                Number(formData.get("longitude")),

            ecosystem_type:
                formData.get("ecosystem_type"),

            area_hectares:
                Number(formData.get("area_hectares")),

            start_date:
                formData.get("start_date"),

            evidence_text:
                formData.get("evidence_text")
        };


        console.log("Sending claim:", payload);


        // ========================================
        // SEND TO FASTAPI
        // ========================================

        try {

            const response = await fetch(
                `${API_BASE}/api/submissions`,
                {
                    method: "POST",

                    headers: {
                        "Content-Type": "application/json"
                    },

                    body: JSON.stringify(payload)
                }
            );


            // Read backend response
            let data = {};

            try {
                data = await response.json();
            }

            catch (error) {
                data = {};
            }


            console.log("Backend response:", data);


            // ========================================
            // HANDLE ERROR
            // ========================================

            if (!response.ok) {

                let message =
                    "The server could not process this claim.";


                if (Array.isArray(data.detail)) {

                    message = data.detail
                        .map(error => {

                            const field = error.loc
                                ? error.loc.join(" → ")
                                : "field";

                            return `${field}: ${error.msg}`;

                        })
                        .join("\n");
                }

                else if (
                    typeof data.detail === "string"
                ) {

                    message = data.detail;
                }

                else if (data.message) {

                    message = data.message;
                }


                throw new Error(message);
            }


            // ========================================
            // SHOW RESULT
            // ========================================

            showResult(data);


            // Clear form
            claimForm.reset();


        }

        catch (error) {

            console.error(
                "BlueVerify submission error:",
                error
            );


            if (resultContainer) {

                resultContainer.classList.add("show");

                resultContainer.innerHTML = `

                    <div class="result-box">

                        <div class="result-header">

                            <div>

                                <p class="section-label">
                                    VERIFICATION ERROR
                                </p>

                                <h2>
                                    Verification failed
                                </h2>

                                <p>
                                    ${escapeHtml(
                                        error.message
                                    )}
                                </p>

                            </div>

                            <div class="result-status warning">
                                ERROR
                            </div>

                        </div>

                    </div>
                `;
            }
        }


        // ========================================
        // ENABLE BUTTON AGAIN
        // ========================================

        finally {

            if (submitButton) {

                submitButton.disabled = false;

                submitButton.textContent =
                    originalButtonText;
            }
        }

    });

}



// ========================================
// DISPLAY VERIFICATION RESULT
// ========================================
function showResult(data) {

    if (!resultContainer) {
        return;
    }

    // Make result visible
    resultContainer.classList.add("show");

    // ========================================
    // GET RESPONSE VALUES
    // ========================================

    const claimId = data.id ?? "—";

    const score = data.ai_score;

    const risk = data.ai_risk_level ?? "Not Available";

    const explanation =
        data.ai_explanation ??
        "AI analysis is not available.";

    const duplicateRisk =
        data.is_duplicate_risk === true;

    const verificationStatus =
        data.verification_status ?? "Submitted";

    const satelliteStatus =
        data.satellite_status ?? "—";

    const satelliteExplanation =
        data.satellite_explanation ?? "—";

    const ndvi = data.ndvi;

    const ndviStatus =
        data.ndvi_status ?? "—";

    const ndviExplanation =
        data.ndvi_explanation ?? "—";

    const carbon =
        data.estimated_carbon_tco2e;

    const credits =
        data.credits_released;

    const creditStage =
        data.credit_stage ?? "—";

    // ========================================
    // SCORE DISPLAY
    // ========================================

    let displayScore = "—";

    if (
        score !== null &&
        score !== undefined
    ) {
        displayScore = Number(score).toFixed(1);
    }

    // ========================================
    // NDVI DISPLAY
    // ========================================

    let displayNdvi = "—";

    if (
        ndvi !== null &&
        ndvi !== undefined
    ) {
        displayNdvi = Number(ndvi).toFixed(3);
    }

    // ========================================
    // CARBON DISPLAY
    // ========================================

    let displayCarbon = "—";

    if (
        carbon !== null &&
        carbon !== undefined
    ) {
        displayCarbon =
            Number(carbon).toFixed(2);
    }

    // ========================================
    // CREDITS DISPLAY
    // ========================================

    let displayCredits = "—";

    if (
        credits !== null &&
        credits !== undefined
    ) {
        displayCredits =
            Number(credits).toFixed(2);
    }

    // ========================================
    // DUPLICATE STATUS
    // ========================================

    const duplicateText =
        duplicateRisk
            ? "Potential duplicate"
            : "No duplicate detected";

    const duplicateClass =
        duplicateRisk
            ? "duplicate-warning"
            : "duplicate-clear";

    // ========================================
    // STATUS CLASS
    // ========================================

    const statusLower =
        String(verificationStatus).toLowerCase();

    let statusClass = "verified";

    if (
        statusLower.includes("review") ||
        statusLower.includes("pending")
    ) {
        statusClass = "warning";
    }

    // ========================================
    // RESULT HTML
    // ========================================

    resultContainer.innerHTML = `

        <div class="result-box">

            <!-- HEADER -->

            <div class="result-header">

                <div>

                    <p class="section-label">
                        VERIFICATION COMPLETE
                    </p>

                    <h2>
                        Claim #${escapeHtml(
                            String(claimId)
                        )}
                    </h2>

                    <p>
                        Your restoration claim has been
                        analyzed by BlueVerify AI.
                    </p>

                </div>

                <div class="result-status ${statusClass}">
                    ${escapeHtml(
                        String(verificationStatus)
                    )}
                </div>

            </div>


            <!-- SCORE + RISK -->

            <div class="result-main">

                <div class="result-score">

                    <span class="result-score-number">
                        ${escapeHtml(displayScore)}
                    </span>

                    <span>
                        AI Verification Score
                    </span>

                </div>


                <div class="result-risk">

                    <span>
                        RISK LEVEL
                    </span>

                    <strong>
                        ${escapeHtml(
                            String(risk)
                        )}
                    </strong>

                </div>

            </div>


            <!-- CLAIM DETAILS -->

            <div class="result-details">

                <div>
                    <small>
                        LOCATION
                    </small>

                    <strong>
                        ${escapeHtml(
                            String(
                                data.location_name ?? "—"
                            )
                        )}
                    </strong>
                </div>


                <div>
                    <small>
                        ECOSYSTEM
                    </small>

                    <strong>
                        ${escapeHtml(
                            String(
                                data.ecosystem_type ?? "—"
                            )
                        )}
                    </strong>
                </div>


                <div>
                    <small>
                        AREA
                    </small>

                    <strong>
                        ${escapeHtml(
                            String(
                                data.area_hectares ?? "—"
                            )
                        )}
                        ha
                    </strong>
                </div>


                <div>
                    <small>
                        DUPLICATE CHECK
                    </small>

                    <strong class="${duplicateClass}">
                        ${escapeHtml(
                            duplicateText
                        )}
                    </strong>
                </div>

            </div>


            <!-- SATELLITE + NDVI -->

            <div class="result-details">

                <div>
                    <small>
                        SATELLITE CHECK
                    </small>

                    <strong>
                        ${escapeHtml(
                            String(satelliteStatus)
                        )}
                    </strong>
                </div>


                <div>
                    <small>
                        NDVI
                    </small>

                    <strong>
                        ${escapeHtml(displayNdvi)}
                    </strong>
                </div>


                <div>
                    <small>
                        VEGETATION
                    </small>

                    <strong>
                        ${escapeHtml(
                            String(ndviStatus)
                        )}
                    </strong>
                </div>

            </div>


            <!-- AI EXPLANATION -->

            <div class="result-explanation">

                <small>
                    AI ANALYSIS
                </small>

                <p>
                    ${escapeHtml(
                        String(explanation)
                    )}
                </p>

            </div>


            <!-- SATELLITE EXPLANATION -->

            <div class="result-explanation">

                <small>
                    SATELLITE ANALYSIS
                </small>

                <p>
                    ${escapeHtml(
                        String(satelliteExplanation)
                    )}
                </p>

            </div>


            <!-- CARBON CREDITS -->

            <div class="result-explanation">

                <small>
                    CARBON & CREDIT STATUS
                </small>

                <div class="result-details">

                    <div>
                        <small>
                            ESTIMATED CARBON
                        </small>

                        <strong>
                            ${escapeHtml(
                                displayCarbon
                            )}
                            tCO₂e
                        </strong>
                    </div>


                    <div>
                        <small>
                            CREDITS RELEASED
                        </small>

                        <strong>
                            ${escapeHtml(
                                displayCredits
                            )}
                            tCO₂e
                        </strong>
                    </div>


                    <div>
                        <small>
                            CREDIT STAGE
                        </small>

                        <strong>
                            ${escapeHtml(
                                String(creditStage)
                            )}
                        </strong>
                    </div>

                </div>

            </div>

        </div>
    `;

    // Scroll to result

    resultContainer.scrollIntoView({
        behavior: "smooth",
        block: "start"
    });
}



// ========================================
// SECURITY HELPER
// ========================================

function escapeHtml(value) {

    return String(value)

        .replace(/&/g, "&amp;")

        .replace(/</g, "&lt;")

        .replace(/>/g, "&gt;")

        .replace(/"/g, "&quot;")

        .replace(/'/g, "&#039;");
}
// ========================================
// ADMIN DASHBOARD
// ========================================

const submissionTable =
    document.getElementById("submissionTable");


// Store submissions for filtering
let allSubmissions = [];


// ========================================
// LOAD SUBMISSIONS
// ========================================

async function loadSubmissions() {

    if (!submissionTable) {
        return;
    }

    submissionTable.innerHTML = `
        <tr>
            <td colspan="13">
                Loading submissions...
            </td>
        </tr>
    `;

    try {

        const response = await fetch(
            `${API_BASE}/api/submissions`
        );

        if (!response.ok) {
            throw new Error(
                `Server error: ${response.status}`
            );
        }

        const data = await response.json();

        console.log(
            "Admin submissions:",
            data
        );

        allSubmissions = data;

        displaySubmissions(allSubmissions);

        updateStatistics(allSubmissions);

    }

    catch (error) {

        console.error(
            "Failed to load submissions:",
            error
        );

        submissionTable.innerHTML = `
            <tr>
                <td colspan="13">
                    Failed to load submissions.
                    <br>
                    ${escapeHtml(error.message)}
                </td>
            </tr>
        `;
    }
}


// ========================================
// DISPLAY SUBMISSIONS
// ========================================
function displaySubmissions(submissions) {

    if (!submissionTable) {
        return;
    }

    if (!submissions.length) {
        submissionTable.innerHTML = `
            <tr>
                <td colspan="13">
                    No submissions found.
                </td>
            </tr>
        `;
        return;
    }

    submissionTable.innerHTML =
        submissions.map(submission => {

            const score =
                submission.ai_score !== null &&
                submission.ai_score !== undefined
                    ? Number(submission.ai_score).toFixed(1)
                    : "—";

            const risk =
                submission.ai_risk_level ??
                "Not Available";

            const duplicate =
                submission.is_duplicate_risk
                    ? "Duplicate Risk"
                    : "Clear";

            const status =
                submission.verification_status ??
                "Pending";

            return `
                <tr>
                    <td>
                        ${escapeHtml(String(submission.id))}
                    </td>

                    <td>
                        ${escapeHtml(
                            String(submission.org_name ?? "—")
                        )}
                    </td>

                    <td>
                        ${escapeHtml(
                            String(submission.ecosystem_type ?? "—")
                        )}
                    </td>

                    <td>
                        ${escapeHtml(
                            String(submission.area_hectares ?? "—")
                        )} ha
                    </td>

                    <td>
                        ${escapeHtml(score)}
                    </td>

                    <td>
                        ${submission.ndvi ?? "—"}
                    </td>
                    <td>
                    ${
                        submission.estimated_carbon_tco2e !== null &&
                        submission.estimated_carbon_tco2e !== undefined
                            ? Number(submission.estimated_carbon_tco2e).toFixed(2)
                            : "—"
                    }
                    </td>
                    <td>
                        ${
                            submission.credits_released !== null &&
                            submission.credits_released !== undefined
                                ? Number(submission.credits_released).toFixed(2)
                                : "—"
                        }
                    </td>

                    <td>
                        ${escapeHtml(submission.credit_stage ?? "—")}
                    </td>
                    <td>
                        ${escapeHtml(risk)}
                    </td>

                    <td>
                        ${escapeHtml(duplicate)}
                    </td>

                    <td>
                        ${escapeHtml(status)}
                    </td>

                    <td>
                        <button
                            class="view-button"
                            onclick="viewClaim(${submission.id})"
                        >
                            View
                        </button>
                    </td>
                </tr>
            `;
        }).join("");
}


// ========================================
// UPDATE STATISTICS
// ========================================
function updateStatistics(submissions) {

    const totalElement =
        document.getElementById(
            "totalSubmissions"
        );

    const pendingElement =
        document.getElementById(
            "pendingStatus"
        );

    const verifiedElement =
        document.getElementById(
            "verifiedStatus"
        );

    const reviewElement =
        document.getElementById(
            "needsReviewStatus"
        );

    const carbonElement =
        document.getElementById(
            "estimatedCarbon"
        );


    // ========================================
    // TOTAL
    // ========================================

    const total =
        submissions.length;


    // ========================================
    // PENDING
    // ========================================

    const pending =
        submissions.filter(
            submission =>
                String(
                    submission.verification_status
                ).toLowerCase() === "pending"
        ).length;


    // ========================================
    // VERIFIED
    // ========================================

    const verified =
        submissions.filter(
            submission =>
                String(
                    submission.verification_status
                ).toLowerCase() === "verified"
        ).length;


    // ========================================
    // NEEDS REVIEW
    // ========================================

    const needsReview =
        submissions.filter(
            submission => {

                const status =
                    String(
                        submission.verification_status ?? ""
                    ).toLowerCase();

                return status === "needs review";
            }
        ).length;


    // ========================================
    // TOTAL ESTIMATED CARBON
    // ========================================

    const totalCarbon =
        submissions.reduce(
            (sum, submission) => {

                const carbon =
                    Number(
                        submission.estimated_carbon_tco2e ?? 0
                    );

                return sum + carbon;
            },
            0
        );


    // ========================================
    // UPDATE DASHBOARD
    // ========================================

    if (totalElement) {
        totalElement.textContent = total;
    }

    if (pendingElement) {
        pendingElement.textContent = pending;
    }

    if (verifiedElement) {
        verifiedElement.textContent = verified;
    }

    if (reviewElement) {
        reviewElement.textContent = needsReview;
    }

    if (carbonElement) {
        carbonElement.textContent =
            totalCarbon.toFixed(2) + " t";
    }
}

// ========================================
// FILTER SUBMISSIONS
// ========================================

function filterSubmissions() {

    const riskFilter =
        document.getElementById(
            "riskFilter"
        );

    const duplicateFilter =
        document.getElementById(
            "duplicateFilter"
        );


    const selectedRisk =
        riskFilter
            ? riskFilter.value
            : "All";


    const selectedDuplicate =
        duplicateFilter
            ? duplicateFilter.value
            : "All";


    const filtered =
        allSubmissions.filter(
            submission => {

                const risk =
                    submission.ai_risk_level ??
                    "Not Available";


                const isDuplicate =
                    submission.is_duplicate_risk === true;


                const riskMatches =
                    selectedRisk === "All" ||
                    String(risk).toLowerCase() ===
                    selectedRisk.toLowerCase();


                const duplicateMatches =
                    selectedDuplicate === "All" ||

                    (
                        selectedDuplicate === "Duplicate" &&
                        isDuplicate
                    ) ||

                    (
                        selectedDuplicate === "Clear" &&
                        !isDuplicate
                    );


                return (
                    riskMatches &&
                    duplicateMatches
                );
            }
        );


    displaySubmissions(filtered);
}


// ========================================
// VIEW CLAIM
// ========================================

function viewClaim(id) {

    const submission = allSubmissions.find(
        submission => submission.id === id
    );

    if (!submission) {
        return;
    }

    const claimDetails = document.getElementById("claimDetails");

    if (!claimDetails) {
        return;
    }

    claimDetails.innerHTML = `
        <h3>Submission #${escapeHtml(String(submission.id))}</h3>

        <p>
            <strong>Submitter:</strong>
            ${escapeHtml(submission.submitter_name ?? "—")}
        </p>

        <p>
            <strong>Organization:</strong>
            ${escapeHtml(submission.org_name ?? "—")}
        </p>

        <p>
            <strong>Location:</strong>
            ${escapeHtml(submission.location_name ?? "—")}
        </p>

        <p>
            <strong>Coordinates:</strong>
            ${escapeHtml(String(submission.latitude ?? "—"))},
            ${escapeHtml(String(submission.longitude ?? "—"))}
        </p>

        <p>
            <strong>Ecosystem:</strong>
            ${escapeHtml(submission.ecosystem_type ?? "—")}
        </p>

        <p>
            <strong>Area:</strong>
            ${escapeHtml(String(submission.area_hectares ?? "—"))} ha
        </p>

        <p>
            <strong>Start Date:</strong>
            ${escapeHtml(String(submission.start_date ?? "—"))}
        </p>

        <p>
            <strong>Evidence:</strong>
            ${escapeHtml(submission.evidence_text ?? "—")}
        </p>

        <hr>

        <h4>AI Verification</h4>

        <p>
            <strong>AI Score:</strong>
            ${
                submission.ai_score !== null &&
                submission.ai_score !== undefined
                    ? Number(submission.ai_score).toFixed(1)
                    : "—"
            }
        </p>

        <p>
            <strong>AI Risk:</strong>
            ${escapeHtml(submission.ai_risk_level ?? "Not Available")}
        </p>

        <p>
            <strong>AI Explanation:</strong>
            ${escapeHtml(submission.ai_explanation ?? "—")}
        </p>

        <hr>

        <h4>Satellite Verification</h4>

        <p>
            <strong>Satellite Status:</strong>
            ${escapeHtml(submission.satellite_status ?? "—")}
        </p>

        <p>
            <strong>Coastal Match:</strong>
            ${
                submission.coastal_match === true
                    ? "Yes"
                    : submission.coastal_match === false
                        ? "No"
                        : "Not Applicable"
            }
        </p>

        <p>
            <strong>Satellite Explanation:</strong>
            ${escapeHtml(submission.satellite_explanation ?? "—")}
        </p>

        <hr>

        <h4>NDVI Verification</h4>

        <p>
            <strong>NDVI:</strong>
            ${
                submission.ndvi !== null &&
                submission.ndvi !== undefined
                    ? Number(submission.ndvi).toFixed(3)
                    : "Not available"
            }
        </p>

        <p>
            <strong>NDVI Status:</strong>
            ${escapeHtml(submission.ndvi_status ?? "Not available")}
        </p>

        <p>
            <strong>NDVI Explanation:</strong>
            ${escapeHtml(submission.ndvi_explanation ?? "Not available")}
        </p>


<hr>

<h4>Carbon Credits</h4>

<p>
    <strong>Estimated Carbon:</strong>
    ${
        submission.estimated_carbon_tco2e !== null &&
        submission.estimated_carbon_tco2e !== undefined
            ? Number(submission.estimated_carbon_tco2e).toFixed(2)
            : "—"
    } tCO₂e
</p>

<p>
    <strong>Credits Released:</strong>
    ${
        submission.credits_released !== null &&
        submission.credits_released !== undefined
            ? Number(submission.credits_released).toFixed(2)
            : "—"
    } tCO₂e
</p>

<p>
    <strong>Credit Stage:</strong>
    ${escapeHtml(submission.credit_stage ?? "—")}
</p>

${
    submission.verification_status === "Verified"
        ? `
            <div class="credit-controls">
                <strong>Advance Credit Stage:</strong>

                <div style="margin-top: 10px;">
                    <button
                        onclick="updateCreditStage(${submission.id}, 'Stage 1')"
                    >
                        Stage 1
                    </button>

                    <button
                        onclick="updateCreditStage(${submission.id}, 'Stage 2')"
                    >
                        Stage 2
                    </button>

                    <button
                        onclick="updateCreditStage(${submission.id}, 'Stage 3')"
                    >
                        Stage 3
                    </button>
                </div>
            </div>
        `
        : `
            <p>
                <strong>Credit Release:</strong>
                On hold until the claim is verified.
            </p>
        `
}

        <hr>

        <h4>Verification Status</h4>

        <p>
            <strong>Status:</strong>
            ${escapeHtml(submission.verification_status ?? "Pending")}
        </p>

        <p>
            <strong>Duplicate Risk:</strong>
            ${
                submission.is_duplicate_risk
                    ? "Yes"
                    : "No"
            }
        </p>

        ${
            submission.duplicate_of_id
                ? `
                    <p>
                        <strong>Duplicate Of:</strong>
                        #${escapeHtml(
                            String(submission.duplicate_of_id)
                        )}
                    </p>
                `
                : ""
        }
    `;
}
async function updateCreditStage(id, stage) {

    try {

        const response = await fetch(
            `${API_BASE}/api/submissions/${id}/credit-stage?stage=${encodeURIComponent(stage)}`,
            {
                method: "PUT"
            }
        );

        const data = await response.json();

        if (!response.ok) {
            alert(data.detail || "Failed to update credit stage.");
            return;
        }

        alert(
            `Credit stage updated!\n\n` +
            `Stage: ${data.credit_stage}\n` +
            `Credits Released: ${data.credits_released} tCO₂e`
        );

        // Reload dashboard data
        await loadSubmissions();

        // Refresh the currently opened claim
        viewClaim(id);

    } catch (error) {

        console.error("Credit stage error:", error);

        alert("Could not update credit stage.");
    }
}

// ========================================
// LOAD ADMIN DATA WHEN PAGE OPENS
// ========================================

if (submissionTable) {

    loadSubmissions();

}