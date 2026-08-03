package com.checksheet.android.ui.history

/**
 * The backend's real ChecksheetStatus enum (app/schemas/checksheet_header.py) is only
 * DRAFT, SUBMITTED, UNDER_REVIEW, APPROVED, REJECTED - there is no SIGNED and no NEEDS_CORRECTION
 * anywhere in the backend. Per explicit direction, this maps onto the requested Android vocabulary
 * without any backend change: APPROVED is presented as "Signed" (consistent with Module 16's
 * precedent that signature is a friendly label over APPROVED, since no real signing backend
 * exists). NEEDS_CORRECTION is kept as a genuinely forward-compatible slot - [deriveLifecycleStatus]
 * never produces it from real data today, exactly like this module's own "unknown status -> UNKNOWN,
 * never crash" instruction already anticipates for values the backend doesn't send.
 */
enum class ChecksheetLifecycleStatus {
    SUBMITTED,
    UNDER_REVIEW,
    SIGNED,
    REJECTED,
    NEEDS_CORRECTION,
    UNKNOWN
}

fun deriveLifecycleStatus(rawStatus: String?): ChecksheetLifecycleStatus =
    when (rawStatus?.trim()?.uppercase()) {
        "SUBMITTED" -> ChecksheetLifecycleStatus.SUBMITTED
        "UNDER_REVIEW" -> ChecksheetLifecycleStatus.UNDER_REVIEW
        "APPROVED" -> ChecksheetLifecycleStatus.SIGNED
        "REJECTED" -> ChecksheetLifecycleStatus.REJECTED
        else -> ChecksheetLifecycleStatus.UNKNOWN
    }
