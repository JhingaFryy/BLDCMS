package com.checksheet.android.util

import android.util.Log
import com.checksheet.android.BuildConfig

/**
 * Thin wrapper around [Log] that is a no-op in release builds. Centralizes the debug/release gate
 * in one place instead of scattering `if (BuildConfig.DEBUG)` checks - release builds must not emit
 * verbose logs (never log password/OTP/JWT/Authorization header values through this or any logger).
 */
object AppLogger {
    fun d(tag: String, message: String) {
        if (BuildConfig.DEBUG) {
            Log.d(tag, message)
        }
    }

    fun e(tag: String, message: String, throwable: Throwable? = null) {
        if (BuildConfig.DEBUG) {
            Log.e(tag, message, throwable)
        }
    }
}
