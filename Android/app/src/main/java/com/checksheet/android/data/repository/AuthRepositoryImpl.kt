package com.checksheet.android.data.repository

import com.checksheet.android.data.api.AuthApi
import com.checksheet.android.data.model.LoginRequest
import com.checksheet.android.data.model.LoginResponse
import com.checksheet.android.data.model.LogoutResponse
import com.checksheet.android.data.model.OpenApiDocument
import com.checksheet.android.data.model.OtpVerificationRequest
import com.checksheet.android.data.model.ServerStatusResponse
import com.checksheet.android.data.model.TokenResponse
import com.checksheet.android.data.model.UserProfileResponse
import com.checksheet.android.domain.repository.AuthRepository
import javax.inject.Inject

class AuthRepositoryImpl @Inject constructor(
    private val authApi: AuthApi
) : AuthRepository {
    override suspend fun login(request: LoginRequest): LoginResponse = authApi.login(request)

    override suspend fun resendOtp(request: LoginRequest): LoginResponse = authApi.login(request)

    override suspend fun verifyOtp(request: OtpVerificationRequest): TokenResponse =
        authApi.verifyOtp(request)

    override suspend fun getUserProfile(): UserProfileResponse = authApi.getUserProfile()

    override suspend fun logout(): LogoutResponse = authApi.logout()

    override suspend fun acknowledgeDeviceNotice() = authApi.acknowledgeDeviceNotice()

    override suspend fun getServerStatus(): ServerStatusResponse = authApi.getServerStatus()

    override suspend fun getOpenApiDocument(): OpenApiDocument = authApi.getOpenApiDocument()
}
