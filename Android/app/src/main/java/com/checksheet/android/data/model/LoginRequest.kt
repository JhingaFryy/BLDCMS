package com.checksheet.android.data.model

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class LoginRequest(
    @SerialName("employee_id") val employeeId: String,
    val password: String,
    @SerialName("device_type") val deviceType: String = "ANDROID",
    @SerialName("device_name") val deviceName: String? = null,
    @SerialName("ip_address") val ipAddress: String? = null,
    @SerialName("user_agent") val userAgent: String? = null,
    // Module 44: optional device-management metadata - see util/DeviceInfoProvider.kt for what
    // populates these and why. Backward compatible: the backend defaults every one of these to
    // null if omitted.
    @SerialName("device_id") val deviceId: String? = null,
    val manufacturer: String? = null,
    @SerialName("device_model") val deviceModel: String? = null,
    @SerialName("os_version") val osVersion: String? = null,
    @SerialName("app_version") val appVersion: String? = null,
    @SerialName("battery_level") val batteryLevel: Int? = null,
    @SerialName("network_type") val networkType: String? = null,
    @SerialName("storage_free_mb") val storageFreeMb: Int? = null,
    @SerialName("storage_total_mb") val storageTotalMb: Int? = null
)
