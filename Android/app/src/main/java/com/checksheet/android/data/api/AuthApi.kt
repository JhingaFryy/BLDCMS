package com.checksheet.android.data.api

import com.checksheet.android.data.model.LoginRequest
import com.checksheet.android.data.model.LoginResponse
import com.checksheet.android.data.model.LogoutResponse
import com.checksheet.android.data.model.OpenApiDocument
import com.checksheet.android.data.model.OtpVerificationRequest
import com.checksheet.android.data.model.ServerStatusResponse
import com.checksheet.android.data.model.TokenResponse
import com.checksheet.android.data.model.UserProfileResponse
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST

interface AuthApi {
    @POST("/mobile-auth/login")
    suspend fun login(@Body request: LoginRequest): LoginResponse

    @POST("/mobile-auth/verify-otp")
    suspend fun verifyOtp(@Body request: OtpVerificationRequest): TokenResponse

    @GET("/auth/me")
    suspend fun getUserProfile(): UserProfileResponse

    @POST("/auth/logout")
    suspend fun logout(): LogoutResponse

    /** Module 44: called once, when the technician dismisses the one-time in-app notice
     * explaining what IT can see/manage on this device - records a real, disclosed
     * acknowledgment server-side (device_info.disclosure_acknowledged_at). */
    @POST("/auth/acknowledge-device-notice")
    suspend fun acknowledgeDeviceNotice()

    /** Root endpoint - no auth required, used only as a lightweight reachability check from the
     * Settings screen's "Test Connection" button. */
    @GET("/")
    suspend fun getServerStatus(): ServerStatusResponse

    /** FastAPI's auto-generated schema document - read only for its `info.version` field, to show
     * a best-effort "Backend Version" on the Settings screen. */
    @GET("/openapi.json")
    suspend fun getOpenApiDocument(): OpenApiDocument
}
