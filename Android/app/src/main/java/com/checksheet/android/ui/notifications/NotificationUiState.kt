package com.checksheet.android.ui.notifications

data class NotificationItem(
    val id: Int,
    val title: String,
    val message: String,
    val type: NotificationType,
    val createdAtDisplay: String,
    val isRead: Boolean,
    val checksheetId: Int?
)

data class NotificationUiState(
    val loading: Boolean = true,
    val items: List<NotificationItem> = emptyList(),
    val unreadCount: Int = 0,
    val errorMessage: String? = null
)
