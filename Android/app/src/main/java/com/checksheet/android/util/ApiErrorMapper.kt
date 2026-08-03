package com.checksheet.android.util

import kotlinx.serialization.SerializationException
import retrofit2.HttpException
import java.io.IOException

private val DEFAULT_HTTP_MESSAGES = mapOf(
    400 to "Invalid request. Please check the details and try again.",
    401 to "Your session has expired. Please log in again.",
    403 to "You do not have permission to perform this action.",
    404 to "The requested information was not found.",
    409 to "This request conflicts with the current data. Please refresh and try again.",
    422 to "Some information is invalid. Please check and try again.",
    429 to "Too many requests. Please wait a moment and try again.",
    500 to "Server error. Please try again later.",
    502 to "Service temporarily unavailable. Please try again later.",
    503 to "Service temporarily unavailable. Please try again later.",
    504 to "Service temporarily unavailable. Please try again later."
)

/**
 * Single source of truth for turning a network exception into a user-facing message - replaces the
 * per-screen `when (e.code()) { ... }` blocks that used to duplicate this table (and, for any
 * unlisted code, used to fall back to the raw Retrofit/OkHttp exception message).
 *
 * [overrides] lets a call site give a status code a more precise meaning than the generic default -
 * e.g. Login/OTP's 401 means "wrong credentials", not "session expired". [defaultMessage] replaces
 * the generic fallback for codes with no specific mapping (e.g. a PDF screen may prefer
 * "Unable to load PDF." over the generic "Something went wrong.").
 */
fun mapApiError(
    throwable: Throwable,
    overrides: Map<Int, String> = emptyMap(),
    defaultMessage: String? = null
): String = when (throwable) {
    is HttpException -> overrides[throwable.code()]
        ?: DEFAULT_HTTP_MESSAGES[throwable.code()]
        ?: defaultMessage
        ?: "Something went wrong. Please try again."
    is IOException -> "Network unavailable. Please check your connection."
    is SerializationException -> "Unexpected response from the server."
    else -> defaultMessage ?: "Something went wrong. Please try again."
}
