package com.checksheet.android.data.model

import kotlinx.serialization.Serializable

@Serializable
data class PaginatedUsersResponse(
    val items: List<UserSummary>,
    val total: Int
)
