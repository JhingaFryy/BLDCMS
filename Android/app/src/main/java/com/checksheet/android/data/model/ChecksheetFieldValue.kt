package com.checksheet.android.data.model

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class ChecksheetFieldValue(
    @SerialName("field_id") val fieldId: Int,
    val value: String
)
