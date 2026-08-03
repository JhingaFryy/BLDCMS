package com.checksheet.android.ui.home

import com.checksheet.android.data.model.UserProfileResponse

data class HomeUiState(
    val loading: Boolean = true,
    val user: UserProfileResponse? = null,
    val errorMessage: String? = null,
    val unreadNotificationCount: Int = 0,
    // Module 44: true until the technician dismisses the one-time device-management disclosure
    // notice (see ui/common/DeviceManagementNoticeDialog.kt) - shown at most once per device.
    val showDeviceManagementNotice: Boolean = false
)
