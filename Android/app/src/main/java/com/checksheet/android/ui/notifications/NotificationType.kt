package com.checksheet.android.ui.notifications

enum class NotificationType {
    CHECKSHEET_SUBMITTED,
    CHECKSHEET_SIGNED,
    CHECKSHEET_REJECTED,
    CHECKSHEET_NEEDS_CORRECTION,
    SYSTEM,
    UNKNOWN
}

/** Any raw type the backend doesn't (yet) send resolves to UNKNOWN rather than crashing. */
fun deriveNotificationType(rawType: String?): NotificationType =
    when (rawType?.trim()?.uppercase()) {
        "CHECKSHEET_SUBMITTED" -> NotificationType.CHECKSHEET_SUBMITTED
        "CHECKSHEET_SIGNED" -> NotificationType.CHECKSHEET_SIGNED
        "CHECKSHEET_REJECTED" -> NotificationType.CHECKSHEET_REJECTED
        "CHECKSHEET_NEEDS_CORRECTION" -> NotificationType.CHECKSHEET_NEEDS_CORRECTION
        "SYSTEM" -> NotificationType.SYSTEM
        else -> NotificationType.UNKNOWN
    }

/** Human-readable category label shown on each notification row. */
fun notificationTypeLabel(type: NotificationType): String = when (type) {
    NotificationType.CHECKSHEET_SUBMITTED -> "Checksheet Submitted"
    NotificationType.CHECKSHEET_SIGNED -> "Checksheet Approved"
    NotificationType.CHECKSHEET_REJECTED -> "Checksheet Rejected"
    NotificationType.CHECKSHEET_NEEDS_CORRECTION -> "Correction Required"
    NotificationType.SYSTEM -> "System Announcement"
    NotificationType.UNKNOWN -> "General Information"
}
