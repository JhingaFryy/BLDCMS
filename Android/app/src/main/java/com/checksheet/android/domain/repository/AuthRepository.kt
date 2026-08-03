package com.checksheet.android.domain.repository

import com.checksheet.android.data.model.LoginRequest
import com.checksheet.android.data.model.LoginResponse
import com.checksheet.android.data.model.LogoutResponse
import com.checksheet.android.data.model.OpenApiDocument
import com.checksheet.android.data.model.OtpVerificationRequest
import com.checksheet.android.data.model.ServerStatusResponse
import com.checksheet.android.data.model.TokenResponse
import com.checksheet.android.data.model.UserProfileResponse

interface AuthRepository {
    suspend fun login(request: LoginRequest): LoginResponse

    suspend fun resendOtp(request: LoginRequest): LoginResponse

    suspend fun verifyOtp(request: OtpVerificationRequest): TokenResponse

    suspend fun getUserProfile(): UserProfileResponse

    suspend fun logout(): LogoutResponse

    suspend fun acknowledgeDeviceNotice()

    /** Lightweight, unauthenticated reachability check for Settings > Test Connection. */
    suspend fun getServerStatus(): ServerStatusResponse

    /** Raw passthrough - the caller decides how to handle a missing/failed version lookup. */
    suspend fun getOpenApiDocument(): OpenApiDocument
}
