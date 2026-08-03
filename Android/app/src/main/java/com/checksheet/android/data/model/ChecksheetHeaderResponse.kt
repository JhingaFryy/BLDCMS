package com.checksheet.android.data.model

import kotlinx.serialization.Serializable

/**
 * The backend's ChecksheetHeaderDetailResponse has many more fields (technician_mobile, created_at,
 * values, etc.) - only [id] is needed here (to support re-saving the same draft via PUT instead of
 * creating duplicates), and the shared Json config (ignoreUnknownKeys = true) safely discards the rest.
 */
@Serializable
data class ChecksheetHeaderResponse(
    val id: Int
)
