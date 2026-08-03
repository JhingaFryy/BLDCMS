package com.checksheet.android.util

import java.text.SimpleDateFormat
import java.util.Locale
import java.util.TimeZone

/** Best-effort formatting of a backend ISO-8601 UTC timestamp into a readable local string. Never
 * throws - falls back to the raw value if parsing fails. */
fun formatBackendTimestamp(raw: String?): String {
    if (raw.isNullOrBlank()) return "-"
    return try {
        val parser = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss", Locale.US)
        parser.timeZone = TimeZone.getTimeZone("UTC")
        val date = parser.parse(raw.substringBefore("."))
        val formatter = SimpleDateFormat("dd MMM yyyy, HH:mm", Locale.US)
        date?.let { formatter.format(it) } ?: raw
    } catch (e: Exception) {
        raw
    }
}

/** Same parsing as [formatBackendTimestamp], but always renders in Asia/Kolkata regardless of the
 * device's own timezone, matching the Dashboard's formatIST() convention. Never throws - falls back
 * to the raw value if parsing fails. */
fun formatBackendTimestampIST(raw: String?): String {
    if (raw.isNullOrBlank()) return "-"
    return try {
        val parser = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss", Locale.US)
        parser.timeZone = TimeZone.getTimeZone("UTC")
        val date = parser.parse(raw.substringBefore("."))
        val formatter = SimpleDateFormat("dd MMM yyyy, hh:mm a", Locale.US)
        formatter.timeZone = TimeZone.getTimeZone("Asia/Kolkata")
        date?.let { "${formatter.format(it)} IST" } ?: raw
    } catch (e: Exception) {
        raw
    }
}
