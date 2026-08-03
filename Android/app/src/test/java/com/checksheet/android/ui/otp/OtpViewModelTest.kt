package com.checksheet.android.ui.otp

import com.checksheet.android.data.model.LoginRequest
import com.checksheet.android.data.model.LoginResponse
import com.checksheet.android.data.model.LogoutResponse
import com.checksheet.android.data.model.OtpVerificationRequest
import com.checksheet.android.data.model.TokenResponse
import com.checksheet.android.data.model.UserProfileResponse
import com.checksheet.android.domain.repository.AuthRepository
import com.checksheet.android.domain.repository.SessionRepository
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flowOf
import kotlinx.coroutines.test.StandardTestDispatcher
import kotlinx.coroutines.test.advanceUntilIdle
import kotlinx.coroutines.test.resetMain
import kotlinx.coroutines.test.runTest
import kotlinx.coroutines.test.setMain
import org.junit.After
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Before
import org.junit.Test

@OptIn(ExperimentalCoroutinesApi::class)
class OtpViewModelTest {
    private val dispatcher = StandardTestDispatcher()

    private lateinit var authRepository: FakeAuthRepository
    private lateinit var sessionRepository: FakeSessionRepository
    private lateinit var viewModel: OtpViewModel

    @Before
    fun setUp() {
        Dispatchers.setMain(dispatcher)
        authRepository = FakeAuthRepository()
        sessionRepository = FakeSessionRepository()
        viewModel = OtpViewModel(authRepository, sessionRepository)
    }

    @After
    fun tearDown() {
        Dispatchers.resetMain()
    }

    @Test
    fun resendOtp_success_clearsOtpAndRestartsCountdown() = runTest {
        viewModel.resendOtp("emp-1", "secret")
        advanceUntilIdle()

        assertEquals("", viewModel.uiState.value.otp)
        assertEquals("New OTP sent.", viewModel.uiState.value.resendSuccess)
    }

    @Test
    fun resendOtp_http429_showsErrorAndRestartsCountdown() = runTest {
        authRepository.failWith429 = true
        viewModel.resendOtp("emp-1", "secret")
        advanceUntilIdle()

        assertEquals("Please wait before requesting another OTP.", viewModel.uiState.value.errorMessage)
    }

    @Test
    fun verifyOtp_technicianRole_succeedsAndKeepsSession() = runTest {
        authRepository.profileRole = "Technician"
        viewModel.onOtpChanged("123456")
        viewModel.verifyOtp("emp-1")
        advanceUntilIdle()

        assertTrue(viewModel.uiState.value.verificationSuccess)
        assertEquals(null, viewModel.uiState.value.errorMessage)
        assertFalse(sessionRepository.sessionCleared)
    }

    @Test
    fun verifyOtp_adminRole_rejectedAndSessionCleared() = runTest {
        authRepository.profileRole = "Admin"
        viewModel.onOtpChanged("123456")
        viewModel.verifyOtp("emp-1")
        advanceUntilIdle()

        assertFalse(viewModel.uiState.value.verificationSuccess)
        assertEquals(
            "Application access is restricted to Technicians. Please use the Dashboard instead.",
            viewModel.uiState.value.errorMessage
        )
        assertTrue(sessionRepository.sessionCleared)
    }

    @Test
    fun verifyOtp_supervisorRole_rejectedAndSessionCleared() = runTest {
        authRepository.profileRole = "Supervisor"
        viewModel.onOtpChanged("123456")
        viewModel.verifyOtp("emp-1")
        advanceUntilIdle()

        assertFalse(viewModel.uiState.value.verificationSuccess)
        assertTrue(sessionRepository.sessionCleared)
    }

    private class FakeAuthRepository : AuthRepository {
        var failWith429 = false
        var profileRole = "Technician"

        override suspend fun login(request: LoginRequest): LoginResponse {
            if (failWith429) {
                throw retrofit2.HttpException(retrofit2.Response.error<Any>(429, okhttp3.ResponseBody.create(null, "")))
            }
            return LoginResponse(requiresOtp = true, message = "OTP sent")
        }

        override suspend fun resendOtp(request: LoginRequest): LoginResponse {
            if (failWith429) {
                throw retrofit2.HttpException(retrofit2.Response.error<Any>(429, okhttp3.ResponseBody.create(null, "")))
            }
            return LoginResponse(requiresOtp = true, message = "OTP sent")
        }

        override suspend fun verifyOtp(request: OtpVerificationRequest): TokenResponse {
            return TokenResponse(accessToken = "token", tokenType = "bearer")
        }

        override suspend fun getUserProfile(): UserProfileResponse {
            return UserProfileResponse(id = 0, employeeId = "", name = "", role = profileRole)
        }

        override suspend fun logout(): LogoutResponse {
            return LogoutResponse(message = "Logged out successfully")
        }

        override suspend fun getServerStatus(): com.checksheet.android.data.model.ServerStatusResponse {
            return com.checksheet.android.data.model.ServerStatusResponse(status = "Server Running")
        }

        override suspend fun getOpenApiDocument(): com.checksheet.android.data.model.OpenApiDocument {
            return com.checksheet.android.data.model.OpenApiDocument()
        }
    }

    private class FakeSessionRepository : SessionRepository {
        var sessionCleared = false

        override fun getAccessToken(): Flow<String?> = flowOf(null)

        override suspend fun saveAccessToken(token: String) {}

        override suspend fun saveTokenType(type: String) {}

        override fun getTokenType(): Flow<String?> = flowOf(null)

        override suspend fun clearSession() {
            sessionCleared = true
        }

        override fun hasValidSession(): Flow<Boolean> = flowOf(false)
    }
}
