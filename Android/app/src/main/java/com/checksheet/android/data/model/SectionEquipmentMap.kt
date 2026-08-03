package com.checksheet.android.data.model

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class SectionEquipmentMap(
    val id: Int,
    @SerialName("section_id") val sectionId: Int,
    @SerialName("equipment_id") val equipmentId: Int,
    val technology: String,
    @SerialName("is_active") val isActive: Boolean,
    @SerialName("section_name") val sectionName: String? = null,
    @SerialName("equipment_name") val equipmentName: String? = null
)
