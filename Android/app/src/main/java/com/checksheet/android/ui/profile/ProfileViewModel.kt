package com.checksheet.android.ui.profile

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.checksheet.android.domain.repository.AuthRepository
import com.checksheet.android.domain.repository.SessionRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import retrofit2.HttpException
import java.io.IOException
import javax.inject.Inject

@HiltViewModel
class ProfileViewModel @Inject constructor(
    private val authRepository: AuthRepository,
    private val sessionRepository: SessionRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(ProfileUiState())
    val uiState: StateFlow<ProfileUiState> = _uiState.asStateFlow()

    init {
        loadProfile()
    }

    fun retry() {
        loadProfile()
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

    private fun loadProfile() {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(loading = true, errorMessage = null)

            try {
                val profile = authRepository.getUserProfile()
                _uiState.value = ProfileUiState(loading = false, user = profile, errorMessage = null)
            } catch (e: HttpException) {
                _uiState.value = ProfileUiState(
                    loading = false,
                    user = null,
                    errorMessage = "Unable to load profile"
                )
            } catch (e: IOException) {
                _uiState.value = ProfileUiState(
                    loading = false,
                    user = null,
                    errorMessage = "Unable to load profile"
                )
            } catch (e: Exception) {
                _uiState.value = ProfileUiState(
                    loading = false,
                    user = null,
                    errorMessage = "Unable to load profile"
                )
            }
        }
    }
}
