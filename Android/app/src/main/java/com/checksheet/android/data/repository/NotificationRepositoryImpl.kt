package com.checksheet.android.data.repository

import androidx.lifecycle.Lifecycle
import androidx.lifecycle.ProcessLifecycleOwner
import com.checksheet.android.data.api.NotificationApi
import com.checksheet.android.data.model.Notification
import com.checksheet.android.data.model.PaginatedNotificationResponse
import com.checksheet.android.domain.repository.NotificationRepository
import com.checksheet.android.domain.repository.SessionRepository
import com.checksheet.android.notification.SystemNotifier
import com.checksheet.android.util.AppLogger
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.SharedFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asSharedFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.collectLatest
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Owns the app's single notification poll loop (Module 26). Because this class is a Hilt
 * @Singleton, HomeViewModel and NotificationViewModel both observe the exact same [notifications]
 * / [unreadCount] instance instead of each running their own poller - avoiding duplicate network
 * calls when both screens happen to be alive at once. The loop starts/stops itself by observing
 * [SessionRepository.hasValidSession] (see init{}), so it runs for as long as the app process is
 * alive and the user is logged in - including while backgrounded - and clears its state on logout.
 */
@Singleton
class NotificationRepositoryImpl @Inject constructor(
    private val notificationApi: NotificationApi,
    private val sessionRepository: SessionRepository,
    private val systemNotifier: SystemNotifier
) : NotificationRepository {

    companion object {
        // "Configurable interval (30-60s)" per the module spec - one named constant, not a
        // user-facing setting (Settings screen is out of scope for this module).
        private const val POLL_INTERVAL_MS = 45_000L
        private const val TAG = "NotificationSync"
    }

    private val repositoryScope = CoroutineScope(SupervisorJob() + Dispatchers.Default)

    private val _notifications = MutableStateFlow<List<Notification>>(emptyList())
    override val notifications: StateFlow<List<Notification>> = _notifications.asStateFlow()

    private val _unreadCount = MutableStateFlow(0)
    override val unreadCount: StateFlow<Int> = _unreadCount.asStateFlow()

    private val _newNotificationEvents = MutableSharedFlow<Notification>(extraBufferCapacity = 16)
    override val newNotificationEvents: SharedFlow<Notification> = _newNotificationEvents.asSharedFlow()

    @Volatile
    private var latestKnownCreatedAt: String? = null

    init {
        repositoryScope.launch {
            sessionRepository.hasValidSession().collectLatest { valid ->
                if (valid) {
                    runSyncLoop()
                } else {
                    // Logged out (or never logged in yet) - nothing to poll, and any previously
                    // cached list/count must not leak into a different technician's next session.
                    _notifications.value = emptyList()
                    _unreadCount.value = 0
                    latestKnownCreatedAt = null
                }
            }
        }
    }

    override suspend fun getNotifications(): PaginatedNotificationResponse {
        val response = notificationApi.getNotifications(skip = 0, limit = 50)
        _notifications.value = response.items
        _unreadCount.value = response.unreadCount
        latestKnownCreatedAt = response.items.maxOfOrNull { it.createdAt } ?: latestKnownCreatedAt
        return response
    }

    override suspend fun markAsRead(notificationId: Int) {
        var didUpdate = false
        _notifications.update { current ->
            val target = current.firstOrNull { it.id == notificationId }
            if (target == null || target.isRead) {
                current
            } else {
                didUpdate = true
                current.map { if (it.id == notificationId) it.copy(isRead = true) else it }
            }
        }
        if (!didUpdate) return
        _unreadCount.update { maxOf(0, it - 1) }

        try {
            notificationApi.markAsRead(notificationId)
        } catch (e: Exception) {
            // Best-effort - a later poll tick's /unread-count resyncs the authoritative count if
            // this particular call didn't actually reach the server.
            AppLogger.e(TAG, "markAsRead failed", e)
        }
    }

    override suspend fun markAllAsRead() {
        var hadUnread = false
        _notifications.update { current ->
            if (current.any { !it.isRead }) hadUnread = true
            current.map { it.copy(isRead = true) }
        }
        if (!hadUnread) return
        _unreadCount.value = 0

        try {
            notificationApi.markAllAsRead()
        } catch (e: Exception) {
            AppLogger.e(TAG, "markAllAsRead failed", e)
        }
    }

    private suspend fun runSyncLoop() {
        try {
            getNotifications()
        } catch (e: Exception) {
            // Not fatal - pollIncremental() below keeps retrying this same initial load (via the
            // latestKnownCreatedAt == null branch) until it succeeds, satisfying "retry
            // automatically... synchronize pending notifications once connectivity is restored"
            // even when the very first load is what failed.
            AppLogger.e(TAG, "Initial notification load failed", e)
        }

        while (true) {
            delay(POLL_INTERVAL_MS)
            pollIncremental()
        }
    }

    private suspend fun pollIncremental() {
        try {
            _unreadCount.value = notificationApi.getUnreadCount().unreadCount
        } catch (e: Exception) {
            AppLogger.e(TAG, "Poll: unread-count failed", e)
            return
        }

        if (latestKnownCreatedAt == null) {
            try {
                getNotifications()
            } catch (e: Exception) {
                AppLogger.e(TAG, "Poll: retry of initial load failed", e)
            }
            return
        }

        val after = latestKnownCreatedAt ?: return

        try {
            val newItems = notificationApi.getNotificationsSince(after = after)
            if (newItems.isEmpty()) return

            val existingIds = _notifications.value.mapTo(mutableSetOf()) { it.id }
            val genuinelyNew = newItems.filter { it.id !in existingIds }
            if (genuinelyNew.isEmpty()) return

            _notifications.update { genuinelyNew + it }
            latestKnownCreatedAt = genuinelyNew.maxOf { it.createdAt }

            val foreground = isAppInForeground()
            genuinelyNew.sortedBy { it.createdAt }.forEach { item ->
                _newNotificationEvents.emit(item)
                if (!foreground) {
                    systemNotifier.notify(item)
                }
            }
        } catch (e: Exception) {
            // Swallow - next tick retries from the same latestKnownCreatedAt, nothing lost.
            AppLogger.e(TAG, "Poll: since failed", e)
        }
    }

    private suspend fun isAppInForeground(): Boolean = withContext(Dispatchers.Main.immediate) {
        ProcessLifecycleOwner.get().lifecycle.currentState.isAtLeast(Lifecycle.State.STARTED)
    }
}
