package com.checksheet.android.ui.settings

import com.checksheet.android.data.model.UserProfileResponse

enum class ConnectionStatus {
    UNKNOWN,
    CHECKING,
    CONNECTED,
    DISCONNECTED
}

data class SettingsUiState(
    val loading: Boolean = true,
    val user: UserProfileResponse? = null,
    val errorMessage: String? = null,
    val themeMode: ThemeMode = ThemeMode.SYSTEM,
    val isLoggingOut: Boolean = false,
    val loggedOut: Boolean = false,
    val connectionStatus: ConnectionStatus = ConnectionStatus.UNKNOWN,
    val backendVersion: String? = null,
    val snackbarMessage: String? = null
)
