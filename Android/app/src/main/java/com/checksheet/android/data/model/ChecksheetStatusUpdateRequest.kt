package com.checksheet.android.data.model

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class ChecksheetStatusUpdateRequest(
    val status: String,
    @SerialName("rejection_reason") val rejectionReason: String? = null
)
