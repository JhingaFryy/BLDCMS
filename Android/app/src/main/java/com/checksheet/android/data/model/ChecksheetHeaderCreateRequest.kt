package com.checksheet.android.data.model

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class ChecksheetHeaderCreateRequest(
    @SerialName("locomotive_id") val locomotiveId: Int,
    @SerialName("section_id") val sectionId: Int,
    // Module 36: null for a section with no equipment at all (e.g. M6-HR).
    @SerialName("equipment_id") val equipmentId: Int? = null,
    @SerialName("template_id") val templateId: Int,
    @SerialName("work_type") val workType: String,
    // Module 32: null for every equipment other than Traction Motor.
    @SerialName("traction_motor_number") val tractionMotorNumber: String? = null,
    @SerialName("maintenance_type") val maintenanceType: String? = null,
    val status: String = "DRAFT",
    val values: List<ChecksheetFieldValue>
)
