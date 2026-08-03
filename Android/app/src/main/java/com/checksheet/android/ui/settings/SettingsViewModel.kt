package com.checksheet.android.ui.settings

import com.checksheet.android.data.session.SettingsPreferences
import com.checksheet.android.domain.repository.AuthRepository
import com.checksheet.android.domain.repository.SessionRepository
import com.checksheet.android.util.AppLogger
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import retrofit2.HttpException
import java.io.IOException
import javax.inject.Inject

@HiltViewModel
class SettingsViewModel @Inject constructor(
    private val authRepository: AuthRepository,
    private val sessionRepository: SessionRepository,
    private val settingsPreferences: SettingsPreferences
) : ViewModel() {

    private val _uiState = MutableStateFlow(SettingsUiState())
    val uiState: StateFlow<SettingsUiState> = _uiState.asStateFlow()

    init {
        loadProfile()
        observeThemeMode()
        loadBackendVersion()
    }

    fun retry() {
        loadProfile()
    }

    private fun observeThemeMode() {
        viewModelScope.launch {
            settingsPreferences.themeModeFlow.collect { raw ->
                _uiState.value = _uiState.value.copy(themeMode = parseThemeMode(raw))
            }
        }
    }

    fun setThemeMode(mode: ThemeMode) {
        viewModelScope.launch {
            settingsPreferences.saveThemeMode(mode.name)
        }
    }

    private fun loadProfile() {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(loading = true, errorMessage = null)

            try {
                val profile = authRepository.getUserProfile()
                _uiState.value = _uiState.value.copy(loading = false, user = profile, errorMessage = null)
            } catch (e: HttpException) {
                _uiState.value = _uiState.value.copy(loading = false, errorMessage = "Unable to load account details")
            } catch (e: IOException) {
                _uiState.value = _uiState.value.copy(loading = false, errorMessage = "Unable to load account details")
            } catch (e: Exception) {
                _uiState.value = _uiState.value.copy(loading = false, errorMessage = "Unable to load account details")
            }
        }
    }

    /** Best-effort only - a failure here just leaves Backend Version showing "Not available". */
    private fun loadBackendVersion() {
        viewModelScope.launch {
            try {
                val doc = authRepository.getOpenApiDocument()
                _uiState.value = _uiState.value.copy(backendVersion = doc.info?.version)
            } catch (e: Exception) {
                // Silent by design - see kdoc above.
            }
        }
    }

    fun testConnection() {
        if (_uiState.value.connectionStatus == ConnectionStatus.CHECKING) return

        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(connectionStatus = ConnectionStatus.CHECKING)

            try {
                authRepository.getServerStatus()
                _uiState.value = _uiState.value.copy(
                    connectionStatus = ConnectionStatus.CONNECTED,
                    snackbarMessage = "Connected to backend server"
                )
            } catch (e: HttpException) {
                // A real HTTP response (even an error one) still proves the server is reachable.
                _uiState.value = _uiState.value.copy(
                    connectionStatus = ConnectionStatus.CONNECTED,
                    snackbarMessage = "Connected to backend server"
                )
            } catch (e: IOException) {
                AppLogger.e("SettingsViewModel", "Test connection failed", e)
                _uiState.value = _uiState.value.copy(
                    connectionStatus = ConnectionStatus.DISCONNECTED,
                    snackbarMessage = "Server unreachable. Please check your network or server address."
                )
            } catch (e: Exception) {
                AppLogger.e("SettingsViewModel", "Test connection failed", e)
                _uiState.value = _uiState.value.copy(
                    connectionStatus = ConnectionStatus.DISCONNECTED,
                    snackbarMessage = "Unable to reach the server"
                )
            }
        }
    }

    fun onSnackbarShown() {
        _uiState.value = _uiState.value.copy(snackbarMessage = null)
    }

    /**
     * Best-effort server-side session revocation, followed by an unconditional local logout.
     * A failed/unreachable backend call must never trap the user in a logged-in-looking state.
     */
    fun logout() {
        if (_uiState.value.isLoggingOut) return

        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isLoggingOut = true)

            try {
                authRepository.logout()
            } catch (e: HttpException) {
                // Ignore - proceed with local logout regardless of server response.
            } catch (e: IOException) {
                // Ignore - no network shouldn't block local logout.
            } catch (e: Exception) {
                // Ignore - local logout must still complete.
            }

            sessionRepository.clearSession()
            _uiState.value = _uiState.value.copy(isLoggingOut = false, loggedOut = true)
        }
    }
}
