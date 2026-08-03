package com.checksheet.android.data.model

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class Notification(
    val id: Int,
    val title: String,
    val message: String,
    val type: String,
    @SerialName("created_at") val createdAt: String,
    @SerialName("is_read") val isRead: Boolean,
    @SerialName("checksheet_id") val checksheetId: Int? = null
)
