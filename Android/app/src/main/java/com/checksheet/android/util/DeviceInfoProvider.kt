package com.checksheet.android.util

import android.content.Context
import android.net.ConnectivityManager
import android.net.NetworkCapabilities
import android.os.BatteryManager
import android.os.Build
import android.os.StatFs
import android.provider.Settings

/**
 * Module 44: collects the same operational device metadata BL-DCMS already needs for device
 * management (manufacturer/model, OS/app version, battery, network status, storage headroom) -
 * sent once at login/OTP-verify time so the backend's device registry (and the System
 * Administration CLI that reads it) has real data instead of the empty fields it had before this
 * module. Every value here is standard, non-invasive device info that requires no dangerous
 * permission and no user prompt - nothing here reads personal files, contacts, location, or any
 * other app's data.
 */
object DeviceInfoProvider {

    /** A stable per-device identifier (ANDROID_ID) - resets only on factory reset, unique per
     * device+app-signing-key combination. Standard, widely-used identifier for exactly this
     * "which physical device is this" purpose; carries no personal information itself. */
    fun deviceId(context: Context): String? =
        try {
            Settings.Secure.getString(context.contentResolver, Settings.Secure.ANDROID_ID)
        } catch (_: Exception) {
            null
        }

    fun manufacturer(): String = Build.MANUFACTURER

    fun deviceModel(): String = Build.MODEL

    fun osVersion(): String = Build.VERSION.RELEASE ?: Build.VERSION.SDK_INT.toString()

    fun appVersion(context: Context): String? =
        try {
            context.packageManager.getPackageInfo(context.packageName, 0).versionName
        } catch (_: Exception) {
            null
        }

    /** 0-100, or null if unavailable (e.g. no battery reported by the platform). */
    fun batteryLevel(context: Context): Int? =
        try {
            val batteryManager = context.getSystemService(Context.BATTERY_SERVICE) as? BatteryManager
            val level = batteryManager?.getIntProperty(BatteryManager.BATTERY_PROPERTY_CAPACITY)
            level?.takeIf { it in 0..100 }
        } catch (_: Exception) {
            null
        }

    /** "WIFI", "CELLULAR", "OTHER", or "NONE" - never anything more specific than transport
     * type (no SSID, no carrier name, no signal strength). */
    fun networkType(context: Context): String =
        try {
            val cm = context.getSystemService(Context.CONNECTIVITY_SERVICE) as? ConnectivityManager
            val network = cm?.activeNetwork
            val capabilities = network?.let { cm.getNetworkCapabilities(it) }
            when {
                capabilities == null -> "NONE"
                capabilities.hasTransport(NetworkCapabilities.TRANSPORT_WIFI) -> "WIFI"
                capabilities.hasTransport(NetworkCapabilities.TRANSPORT_CELLULAR) -> "CELLULAR"
                else -> "OTHER"
            }
        } catch (_: Exception) {
            "NONE"
        }

    /** Free/total space (in MB) on the partition holding this app's own private storage - never
     * the whole device's storage, and never a listing of what's in it. */
    fun storageFreeMb(context: Context): Int? =
        try {
            val stat = StatFs(context.filesDir.path)
            ((stat.availableBlocksLong * stat.blockSizeLong) / (1024 * 1024)).toInt()
        } catch (_: Exception) {
            null
        }

    fun storageTotalMb(context: Context): Int? =
        try {
            val stat = StatFs(context.filesDir.path)
            ((stat.blockCountLong * stat.blockSizeLong) / (1024 * 1024)).toInt()
        } catch (_: Exception) {
            null
        }
}
