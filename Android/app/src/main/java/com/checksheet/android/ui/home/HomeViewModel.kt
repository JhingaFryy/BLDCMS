package com.checksheet.android.ui.home

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.checksheet.android.data.session.SettingsPreferences
import com.checksheet.android.domain.repository.AuthRepository
import com.checksheet.android.domain.repository.NotificationRepository
import com.checksheet.android.util.AppLogger
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.flow.launchIn
import kotlinx.coroutines.flow.onEach
import kotlinx.coroutines.launch
import retrofit2.HttpException
import java.io.IOException
import javax.inject.Inject

@HiltViewModel
class HomeViewModel @Inject constructor(
    private val authRepository: AuthRepository,
    private val settingsPreferences: SettingsPreferences,
    notificationRepository: NotificationRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(HomeUiState())
    val uiState: StateFlow<HomeUiState> = _uiState.asStateFlow()

    init {
        loadProfile()
        checkDeviceManagementNotice()

        // NotificationRepository's poll loop (Module 26) keeps unreadCount fresh in the background
        // for as long as the app is running - the badge just observes it, no fetch-on-resume hack
        // and no extra network call needed here at all.
        notificationRepository.unreadCount
            .onEach { count -> _uiState.value = _uiState.value.copy(unreadNotificationCount = count) }
            .launchIn(viewModelScope)
    }

    fun retry() {
        loadProfile()
    }

    private fun checkDeviceManagementNotice() {
        viewModelScope.launch {
            val alreadySeen = settingsPreferences.deviceManagementNoticeSeenFlow.first()
            if (!alreadySeen) {
                _uiState.value = _uiState.value.copy(showDeviceManagementNotice = true)
            }
        }
    }

    /** Module 44: called when the technician dismisses the device-management disclosure notice -
     * records the acknowledgment locally (so it never shows again on this device) and, best
     * effort, server-side (device_info.disclosure_acknowledged_at) for real auditability. A
     * failure to reach the server never blocks the technician - the notice has already been
     * shown and dismissed either way, and the local flag is what prevents it reappearing. */
    fun acknowledgeDeviceManagementNotice() {
        _uiState.value = _uiState.value.copy(showDeviceManagementNotice = false)
        viewModelScope.launch {
            settingsPreferences.setDeviceManagementNoticeSeen()
            try {
                authRepository.acknowledgeDeviceNotice()
            } catch (e: Exception) {
                AppLogger.e("HomeViewModel", "Failed to report device-notice acknowledgment: ${e.message}")
            }
        }
    }

    private fun loadProfile() {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(loading = true, errorMessage = null)

            try {
                val profile = authRepository.getUserProfile()
                _uiState.value = _uiState.value.copy(loading = false, user = profile, errorMessage = null)
            } catch (e: HttpException) {
                _uiState.value = _uiState.value.copy(
                    loading = false,
                    user = null,
                    errorMessage = "Unable to load profile. Please try again."
                )
            } catch (e: IOException) {
                _uiState.value = _uiState.value.copy(
                    loading = false,
                    user = null,
                    errorMessage = "Network error. Please check your connection."
                )
            } catch (e: Exception) {
                _uiState.value = _uiState.value.copy(
                    loading = false,
                    user = null,
                    errorMessage = "Unable to load profile. Please try again."
                )
            }
        }
    }
}
