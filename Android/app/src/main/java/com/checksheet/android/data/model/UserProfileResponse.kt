package com.checksheet.android.data.model

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class UserProfileResponse(
    val id: Int,
    @SerialName("employee_id") val employeeId: String,
    val name: String,
    val mobile: String? = null,
    val email: String? = null,
    val role: String? = null,
    @SerialName("section_id") val sectionId: Int? = null,
    @SerialName("section_name") val sectionName: String? = null,
    // Module 44: a System-Administration-CLI-issued command awaiting this device (currently only
    // "CLEAR_APP_DATA") - null when there is nothing pending. See util/DeviceDataClearer.kt.
    @SerialName("pending_admin_command") val pendingAdminCommand: String? = null
)
