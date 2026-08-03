package com.checksheet.android.ui.profile

import com.checksheet.android.data.model.UserProfileResponse

data class ProfileUiState(
    val loading: Boolean = true,
    val user: UserProfileResponse? = null,
    val errorMessage: String? = null,
    val isLoggingOut: Boolean = false,
    val loggedOut: Boolean = false
)
