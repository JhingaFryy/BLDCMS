package com.checksheet.android.ui.otp

import android.content.Context
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.checksheet.android.data.model.LoginRequest
import com.checksheet.android.data.model.OtpVerificationRequest
import com.checksheet.android.domain.repository.AuthRepository
import com.checksheet.android.domain.repository.SessionRepository
import com.checksheet.android.util.AppLogger
import com.checksheet.android.util.DeviceDataClearer
import com.checksheet.android.util.DeviceInfoProvider
import com.checksheet.android.util.mapApiError
import dagger.hilt.android.lifecycle.HiltViewModel
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import retrofit2.HttpException
import java.io.IOException
import javax.inject.Inject

data class OtpUiState(
    val otp: String = "",
    val isLoading: Boolean = false,
    val errorMessage: String? = null,
    val verificationSuccess: Boolean = false,
    val countdownSeconds: Int = 30,
    val canResend: Boolean = false,
    val resendSuccess: String? = null
)

@HiltViewModel
class OtpViewModel @Inject constructor(
    private val authRepository: AuthRepository,
    private val sessionRepository: SessionRepository,
    private val deviceDataClearer: DeviceDataClearer,
    @ApplicationContext private val appContext: Context
) : ViewModel() {

    private val _uiState = MutableStateFlow(OtpUiState())
    val uiState: StateFlow<OtpUiState> = _uiState.asStateFlow()

    private var countdownJob: Job? = null

    init {
        startCountdown()
    }

    fun onOtpChanged(value: String) {
        val sanitized = value.filter { it.isDigit() }.take(6)
        _uiState.value = _uiState.value.copy(otp = sanitized, errorMessage = null)
    }

    private fun startCountdown() {
        countdownJob?.cancel()
        countdownJob = viewModelScope.launch {
            var seconds = 30
            _uiState.value = _uiState.value.copy(countdownSeconds = seconds, canResend = false)

            while (seconds > 0) {
                delay(1000L)
                seconds -= 1
                _uiState.value = _uiState.value.copy(
                    countdownSeconds = seconds,
                    canResend = seconds == 0
                )
            }
        }
    }

    fun resendOtp(employeeId: String, password: String) {
        if (_uiState.value.isLoading) return

        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isLoading = true, errorMessage = null, resendSuccess = null)

            try {
                val response = authRepository.resendOtp(
                    LoginRequest(
                        employeeId = employeeId,
                        password = password,
                        deviceType = "ANDROID",
                        deviceId = DeviceInfoProvider.deviceId(appContext)
                    )
                )

                if (response.requiresOtp) {
                    _uiState.value = _uiState.value.copy(
                        otp = "",
                        isLoading = false,
                        errorMessage = null,
                        resendSuccess = "New OTP sent."
                    )
                    startCountdown()
                } else {
                    _uiState.value = _uiState.value.copy(
                        isLoading = false,
                        errorMessage = "Unexpected response from server",
                        resendSuccess = null
                    )
                    startCountdown()
                }
            } catch (e: HttpException) {
                val message = mapApiError(
                    e,
                    overrides = mapOf(
                        401 to "Invalid Employee ID or Password",
                        429 to "Please wait before requesting another OTP.",
                        500 to "Server error. Please try again later."
                    )
                )
                _uiState.value = _uiState.value.copy(
                    isLoading = false,
                    errorMessage = message,
                    resendSuccess = null,
                    countdownSeconds = 30,
                    canResend = false
                )
                startCountdown()
            } catch (e: IOException) {
                AppLogger.e("OtpViewModel", "IOException ${e.message}")
                _uiState.value = _uiState.value.copy(
                    isLoading = false,
                    errorMessage = "Network error",
                    resendSuccess = null,
                    countdownSeconds = 30,
                    canResend = false
                )
                startCountdown()
            } catch (e: Exception) {
                AppLogger.e("OtpViewModel", "Exception ${e.message}")
                _uiState.value = _uiState.value.copy(
                    isLoading = false,
                    errorMessage = "Request failed",
                    resendSuccess = null,
                    countdownSeconds = 30,
                    canResend = false
                )
                startCountdown()
            }
        }
    }

    fun verifyOtp(employeeId: String) {
        val otp = _uiState.value.otp
        if (otp.length != 6) {
            _uiState.value = _uiState.value.copy(errorMessage = "Enter a 6-digit OTP")
            return
        }

        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isLoading = true, errorMessage = null)
            AppLogger.d("OtpViewModel", "OTP verification request started")

            try {
                val response = authRepository.verifyOtp(
                    OtpVerificationRequest(
                        employeeId = employeeId,
                        otp = otp,
                        deviceType = "ANDROID",
                        deviceId = DeviceInfoProvider.deviceId(appContext),
                        manufacturer = DeviceInfoProvider.manufacturer(),
                        deviceModel = DeviceInfoProvider.deviceModel(),
                        osVersion = DeviceInfoProvider.osVersion(),
                        appVersion = DeviceInfoProvider.appVersion(appContext),
                        batteryLevel = DeviceInfoProvider.batteryLevel(appContext),
                        networkType = DeviceInfoProvider.networkType(appContext),
                        storageFreeMb = DeviceInfoProvider.storageFreeMb(appContext),
                        storageTotalMb = DeviceInfoProvider.storageTotalMb(appContext)
                    )
                )

                sessionRepository.saveAccessToken(response.accessToken)
                sessionRepository.saveTokenType(response.tokenType)
                AppLogger.d("OtpViewModel", "JWT saved to session repository")

                val profile = authRepository.getUserProfile()

                // Module 44: a System Administration CLI operator queued a disclosed app-data
                // clear for this device (e.g. reported lost/stolen) - execute it now, before
                // this login is allowed to proceed, and route back to Login rather than Home.
                // See util/DeviceDataClearer.kt for exactly what is (and is never) touched.
                if (profile.pendingAdminCommand == "CLEAR_APP_DATA") {
                    AppLogger.d("OtpViewModel", "Executing pending admin command: CLEAR_APP_DATA")
                    deviceDataClearer.clearAll(appContext)
                    _uiState.value = _uiState.value.copy(
                        isLoading = false,
                        verificationSuccess = false,
                        errorMessage = "Your organization's IT administrator has cleared this device's " +
                            "app data for security reasons. Please log in again."
                    )
                    return@launch
                }

                if (profile.role == "Admin" || profile.role == "Supervisor") {
                    // This app is Technician-only - Admins and Supervisors use the Dashboard.
                    // No session is kept for them here.
                    AppLogger.d("OtpViewModel", "Login rejected - restricted role ${profile.role}")
                    sessionRepository.clearSession()
                    _uiState.value = _uiState.value.copy(
                        isLoading = false,
                        verificationSuccess = false,
                        errorMessage = "Application access is restricted to Technicians. Please use the Dashboard instead."
                    )
                    return@launch
                }

                _uiState.value = _uiState.value.copy(
                    isLoading = false,
                    verificationSuccess = true,
                    errorMessage = null
                )
            } catch (e: HttpException) {
                val message = mapApiError(
                    e,
                    overrides = mapOf(
                        401 to "Invalid OTP",
                        429 to "Too many attempts",
                        500 to "Server error"
                    )
                )
                AppLogger.e("OtpViewModel", "HTTP ${e.code()} ${e.message()}")
                _uiState.value = _uiState.value.copy(isLoading = false, errorMessage = message)
            } catch (e: IOException) {
                AppLogger.e("OtpViewModel", "IOException ${e.message}")
                _uiState.value = _uiState.value.copy(isLoading = false, errorMessage = "Network error")
            } catch (e: Exception) {
                AppLogger.e("OtpViewModel", "Exception ${e.message}")
                _uiState.value = _uiState.value.copy(isLoading = false, errorMessage = "Verification failed")
            }
        }
    }
}
