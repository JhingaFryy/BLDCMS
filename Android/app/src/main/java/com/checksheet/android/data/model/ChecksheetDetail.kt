package com.checksheet.android.data.model

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

/**
 * Minimal projection of the backend's ChecksheetHeaderDetailResponse - only what the Approval
 * Review screen needs. ignoreUnknownKeys discards the rest (pdf_path, approved_by, etc.).
 */
@Serializable
data class ChecksheetDetail(
    val id: Int,
    @SerialName("locomotive_id") val locomotiveId: Int,
    @SerialName("section_id") val sectionId: Int,
    // Module 36: null for a section with no equipment at all (e.g. M6-HR).
    @SerialName("equipment_id") val equipmentId: Int? = null,
    @SerialName("template_id") val templateId: Int,
    @SerialName("template_name") val templateName: String? = null,
    @SerialName("technician_mobile") val technicianMobile: String,
    // Module 29.8: Supervisor Review screen field list (name/employee id + full locomotive/
    // equipment/section context) - all already returned by the backend's ChecksheetHeaderResponse,
    // just not previously read by this DTO.
    @SerialName("technician_name") val technicianName: String? = null,
    @SerialName("technician_employee_id") val technicianEmployeeId: String? = null,
    @SerialName("locomotive_number") val locomotiveNumber: String? = null,
    @SerialName("locomotive_type") val locomotiveType: String? = null,
    val technology: String? = null,
    @SerialName("equipment_name") val equipmentName: String? = null,
    @SerialName("section_name") val sectionName: String? = null,
    @SerialName("work_type") val workType: String? = null,
    // Module 32: null for every equipment other than Traction Motor.
    @SerialName("traction_motor_number") val tractionMotorNumber: String? = null,
    @SerialName("maintenance_type") val maintenanceType: String? = null,
    val status: String? = null,
    @SerialName("submitted_at") val submittedAt: String? = null,
    @SerialName("last_modified_at") val lastModifiedAt: String? = null,
    @SerialName("approved_at") val approvedAt: String? = null,
    @SerialName("rejection_reason") val rejectionReason: String? = null,
    @SerialName("pdf_path") val pdfPath: String? = null,
    val values: List<ChecksheetFieldValueDetail> = emptyList(),
    // The backend does not send any of these today (verified against app/models, app/schemas,
    // app/api, app/services - no signature/DSC/certificate concept exists anywhere yet). Kept
    // optional so that if a future backend module adds them, this DTO picks them up with zero
    // further Android changes; until then they simply stay null.
    @SerialName("signature_status") val signatureStatus: String? = null,
    @SerialName("signed_by") val signedBy: String? = null,
    @SerialName("signature_date") val signatureDate: String? = null,
    @SerialName("certificate_name") val certificateName: String? = null,
    @SerialName("certificate_authority") val certificateAuthority: String? = null
)
