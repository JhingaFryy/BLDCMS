package com.checksheet.android.ui.splash

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.checksheet.android.domain.repository.AuthRepository
import com.checksheet.android.domain.repository.SessionRepository
import com.checksheet.android.util.AppLogger
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.firstOrNull
import kotlinx.coroutines.launch
import retrofit2.HttpException
import java.io.IOException
import javax.inject.Inject

data class SplashUiState(
    val isLoading: Boolean = true,
    val errorMessage: String? = null,
    val showRetry: Boolean = false,
    val shouldNavigateToLogin: Boolean = false,
    val shouldNavigateToHome: Boolean = false
)

@HiltViewModel
class SplashViewModel @Inject constructor(
    private val sessionRepository: SessionRepository,
    private val authRepository: AuthRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(SplashUiState())
    val uiState: StateFlow<SplashUiState> = _uiState.asStateFlow()

    init {
        checkSession()
    }

    fun checkSession() {
        viewModelScope.launch {
            AppLogger.d("SplashViewModel", "Splash started")
            val token = sessionRepository.getAccessToken().firstOrNull()

            if (token.isNullOrBlank()) {
                AppLogger.d("SplashViewModel", "Token missing")
                _uiState.value = SplashUiState(
                    isLoading = false,
                    shouldNavigateToLogin = true
                )
                return@launch
            }

            AppLogger.d("SplashViewModel", "Token found")
            AppLogger.d("SplashViewModel", "Calling /auth/me")
            _uiState.value = SplashUiState(isLoading = true, errorMessage = null, showRetry = false)

            try {
                val profile = authRepository.getUserProfile()

                // Defense in depth alongside the check in OtpViewModel.verifyOtp() - a stale
                // session saved before this restriction existed (or left behind by a failed
                // post-verification role check) must not reach Home either.
                if (profile.role == "Admin" || profile.role == "Supervisor") {
                    AppLogger.d("SplashViewModel", "Session rejected - restricted role ${profile.role}")
                    sessionRepository.clearSession()
                    _uiState.value = SplashUiState(
                        isLoading = false,
                        shouldNavigateToLogin = true
                    )
                    return@launch
                }

                AppLogger.d("SplashViewModel", "Authentication restored")
                _uiState.value = SplashUiState(
                    isLoading = false,
                    shouldNavigateToHome = true
                )
            } catch (e: HttpException) {
                // Only a 401 actually proves the token/session is invalid - get_current_user() never
                // raises anything else. Any other status (5xx during a deploy, etc.) must leave the
                // still-valid session alone and let the user retry, not force them back to Login.
                if (e.code() == 401) {
                    AppLogger.e("SplashViewModel", "HTTP 401 invalid or expired token")
                    sessionRepository.clearSession()
                    AppLogger.d("SplashViewModel", "Session cleared")
                    _uiState.value = SplashUiState(
                        isLoading = false,
                        shouldNavigateToLogin = true,
                        errorMessage = null
                    )
                } else {
                    AppLogger.e("SplashViewModel", "HTTP ${e.code()} while restoring session")
                    _uiState.value = SplashUiState(
                        isLoading = false,
                        showRetry = true,
                        errorMessage = "Unable to reach the server. Please try again."
                    )
                }
            } catch (e: IOException) {
                AppLogger.e("SplashViewModel", "IOException ${e.message}")
                _uiState.value = SplashUiState(
                    isLoading = false,
                    showRetry = true,
                    errorMessage = "Network error"
                )
            } catch (e: Exception) {
                // Not proof the session itself is invalid (e.g. a malformed response body) - same
                // reasoning as the non-401 HttpException branch above, the session must survive.
                AppLogger.e("SplashViewModel", "Exception ${e.message}")
                _uiState.value = SplashUiState(
                    isLoading = false,
                    showRetry = true,
                    errorMessage = "Something went wrong. Please try again."
                )
            }
        }
    }
}
