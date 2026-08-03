package com.checksheet.android.data.model

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

/**
 * Minimal projection of the backend's ChecksheetHeaderResponse - only what the Pending Approvals
 * list card needs. ignoreUnknownKeys discards the rest.
 */
@Serializable
data class ChecksheetSummary(
    val id: Int,
    @SerialName("locomotive_id") val locomotiveId: Int,
    @SerialName("section_id") val sectionId: Int,
    // Module 36: null for a section with no equipment at all (e.g. M6-HR).
    @SerialName("equipment_id") val equipmentId: Int? = null,
    @SerialName("technician_mobile") val technicianMobile: String,
    @SerialName("work_type") val workType: String? = null,
    val status: String? = null,
    @SerialName("submitted_at") val submittedAt: String? = null,
    @SerialName("created_at") val createdAt: String? = null,
    @SerialName("pdf_path") val pdfPath: String? = null,
    @SerialName("locomotive_number") val locomotiveNumber: String? = null,
    @SerialName("locomotive_type") val locomotiveType: String? = null,
    val technology: String? = null,
    @SerialName("equipment_name") val equipmentName: String? = null,
    @SerialName("section_name") val sectionName: String? = null
)
