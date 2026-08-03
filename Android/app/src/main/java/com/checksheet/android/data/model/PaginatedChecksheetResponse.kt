package com.checksheet.android.data.model

import kotlinx.serialization.Serializable

@Serializable
data class PaginatedChecksheetResponse(
    val items: List<ChecksheetSummary>,
    val total: Int
)
