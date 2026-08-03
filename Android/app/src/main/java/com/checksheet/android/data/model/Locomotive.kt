package com.checksheet.android.data.model

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class Locomotive(
    val id: Int,
    @SerialName("loco_number") val locoNumber: String,
    @SerialName("loco_model") val locoModel: String,
    val technology: String,
    @SerialName("is_active") val isActive: Boolean
)
