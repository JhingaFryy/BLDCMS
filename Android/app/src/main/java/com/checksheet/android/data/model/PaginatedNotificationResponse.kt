package com.checksheet.android.data.model

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class PaginatedNotificationResponse(
    val items: List<Notification>,
    val total: Int,
    @SerialName("unread_count") val unreadCount: Int
)
