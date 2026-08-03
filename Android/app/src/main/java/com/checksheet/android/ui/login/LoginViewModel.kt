package com.checksheet.android.ui.login

import android.content.Context
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.checksheet.android.data.model.LoginRequest
import com.checksheet.android.domain.repository.AuthRepository
import com.checksheet.android.util.AppLogger
import com.checksheet.android.util.DeviceInfoProvider
import com.checksheet.android.util.mapApiError
import dagger.hilt.android.lifecycle.HiltViewModel
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import retrofit2.HttpException
import java.io.IOException
import javax.inject.Inject

data class LoginUiState(
    val employeeId: String = "",
    val password: String = "",
    val isLoading: Boolean = false,
    val errorMessage: String? = null,
    val otpRequested: Boolean = false,
    val requestedEmployeeId: String? = null
)

@HiltViewModel
class LoginViewModel @Inject constructor(
    private val authRepository: AuthRepository,
    @ApplicationContext private val appContext: Context
) : ViewModel() {

    private val _uiState = MutableStateFlow(LoginUiState())
    val uiState: StateFlow<LoginUiState> = _uiState.asStateFlow()

    fun onEmployeeIdChanged(value: String) {
        _uiState.value = _uiState.value.copy(employeeId = value, errorMessage = null)
    }

    fun onPasswordChanged(value: String) {
        _uiState.value = _uiState.value.copy(password = value, errorMessage = null)
    }

    fun requestOtp() {
        if (_uiState.value.isLoading) return

        val employeeId = _uiState.value.employeeId.trim()
        val password = _uiState.value.password

        if (employeeId.isEmpty() || password.isEmpty()) {
            _uiState.value = _uiState.value.copy(errorMessage = "Employee ID and password are required")
            return
        }

        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isLoading = true, errorMessage = null)
            AppLogger.d("LoginViewModel", "POST /mobile-auth/login Employee ID: $employeeId")

            try {
                val response = authRepository.login(
                    LoginRequest(
                        employeeId = employeeId,
                        password = password,
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

                AppLogger.d("LoginViewModel", "HTTP Status ${response.requiresOtp} Response body ${response.message}")

                if (response.requiresOtp) {
                    _uiState.value = _uiState.value.copy(
                        isLoading = false,
                        otpRequested = true,
                        requestedEmployeeId = employeeId,
                        errorMessage = null
                    )
                } else {
                    _uiState.value = _uiState.value.copy(
                        isLoading = false,
                        errorMessage = "Unexpected response from server"
                    )
                }
            } catch (e: HttpException) {
                val message = mapApiError(
                    e,
                    overrides = mapOf(
                        401 to "Invalid Employee ID or Password",
                        429 to "Please wait before requesting another OTP.",
                        500 to "Server error.Please try again later."
                    )
                )
                AppLogger.e("LoginViewModel", "HTTP ${e.code()} ${e.message()}")
                _uiState.value = _uiState.value.copy(isLoading = false, errorMessage = message)
            } catch (e: IOException) {
                AppLogger.e("LoginViewModel", "IOException ${e.message}")
                _uiState.value = _uiState.value.copy(isLoading = false, errorMessage = "Cannot connect to server.")
            } catch (e: Exception) {
                AppLogger.e("LoginViewModel", "Exception ${e.message}")
                _uiState.value = _uiState.value.copy(isLoading = false, errorMessage = "Request failed")
            }
        }
    }
}
