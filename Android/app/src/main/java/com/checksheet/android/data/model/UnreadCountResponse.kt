package com.checksheet.android.data.model

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class UnreadCountResponse(
    @SerialName("unread_count") val unreadCount: Int
)
