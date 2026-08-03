package com.checksheet.android.data.model

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class ChecksheetHeaderUpdateRequest(
    @SerialName("work_type") val workType: String? = null,
    val values: List<ChecksheetFieldValue>? = null
)
