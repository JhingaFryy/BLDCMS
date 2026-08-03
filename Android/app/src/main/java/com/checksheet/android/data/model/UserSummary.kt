package com.checksheet.android.data.model

import kotlinx.serialization.Serializable

/**
 * Minimal projection of the backend's UserResponse - only what's needed to resolve a technician's
 * mobile number into a display name for the Pending Approvals list. ignoreUnknownKeys discards the
 * rest (employee_id, email, is_active, section_id, section_name, created_at, ...).
 */
@Serializable
data class UserSummary(
    val name: String,
    val mobile: String,
    val role: String? = null
)
