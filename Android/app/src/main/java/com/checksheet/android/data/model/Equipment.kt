package com.checksheet.android.data.model

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class Equipment(
    val id: Int,
    @SerialName("equipment_code") val equipmentCode: String,
    @SerialName("equipment_name") val equipmentName: String,
    @SerialName("is_active") val isActive: Boolean,
    @SerialName("used_in") val usedIn: String? = null
)
