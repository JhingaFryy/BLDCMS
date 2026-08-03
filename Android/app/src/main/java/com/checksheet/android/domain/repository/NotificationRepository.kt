package com.checksheet.android.domain.repository

import com.checksheet.android.data.model.Notification
import com.checksheet.android.data.model.PaginatedNotificationResponse
import kotlinx.coroutines.flow.SharedFlow
import kotlinx.coroutines.flow.StateFlow

interface NotificationRepository {
    suspend fun getNotifications(): PaginatedNotificationResponse
    suspend fun markAsRead(notificationId: Int)
    suspend fun markAllAsRead()

    /**
     * Continuously kept in sync by a background poll loop (started/stopped automatically as the
     * session becomes valid/invalid) - reflects the full known notification list, newest first.
     * Both HomeViewModel (badge) and NotificationViewModel (list) observe this same instance, so
     * only one poller ever runs for the whole app process, not one per screen.
     */
    val notifications: StateFlow<List<Notification>>

    /** Authoritative unread count, refreshed on every poll tick via the lightweight endpoint. */
    val unreadCount: StateFlow<Int>

    /** Emits once per genuinely new notification as soon as a poll tick discovers it - used to
     * drive the in-app Snackbar and/or system notification. Never replays past events to a new
     * subscriber (a freshly opened screen must not re-announce notifications that already arrived). */
    val newNotificationEvents: SharedFlow<Notification>
}
