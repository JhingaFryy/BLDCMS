package com.checksheet.android.ui.notifications

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.checksheet.android.data.model.Notification
import com.checksheet.android.domain.repository.NotificationRepository
import com.checksheet.android.util.formatBackendTimestampIST
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.combine
import kotlinx.coroutines.flow.launchIn
import kotlinx.coroutines.flow.onEach
import kotlinx.coroutines.launch
import retrofit2.HttpException
import java.io.IOException
import javax.inject.Inject

/**
 * Sources its list/unread-count purely from NotificationRepository's reactive state (Module 26) -
 * the repository's background poll loop is what actually fetches data, so new notifications show
 * up here automatically without this ViewModel (or NotificationScreen) needing to do anything.
 * refresh()/retry() remain as an explicit manual pull, used for pull-to-refresh and the error
 * Retry button.
 */
@HiltViewModel
class NotificationViewModel @Inject constructor(
    private val notificationRepository: NotificationRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(NotificationUiState())
    val uiState: StateFlow<NotificationUiState> = _uiState.asStateFlow()

    init {
        combine(
            notificationRepository.notifications,
            notificationRepository.unreadCount
        ) { notifications, unreadCount ->
            notifications.map { it.toNotificationItem() } to unreadCount
        }.onEach { (items, unreadCount) ->
            _uiState.value = _uiState.value.copy(
                loading = false,
                items = items,
                unreadCount = unreadCount,
                errorMessage = null
            )
        }.launchIn(viewModelScope)

        // The repository may not have completed its own initial load yet (e.g. this screen opens
        // right after login, before the background poller's first tick finishes) - kick one off
        // explicitly so the user isn't stuck looking at a spinner until the next poll interval.
        if (notificationRepository.notifications.value.isEmpty()) {
            refresh()
        } else {
            _uiState.value = _uiState.value.copy(loading = false)
        }
    }

    fun retry() = refresh()

    fun refresh() {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(loading = true, errorMessage = null)
            try {
                notificationRepository.getNotifications()
                // No need to touch _uiState on success - the combine() collector above picks up
                // the repository's freshly updated state and turns loading back off itself.
            } catch (e: HttpException) {
                _uiState.value = _uiState.value.copy(loading = false, errorMessage = "Unable to load notifications")
            } catch (e: IOException) {
                _uiState.value = _uiState.value.copy(loading = false, errorMessage = "Unable to load notifications")
            } catch (e: Exception) {
                _uiState.value = _uiState.value.copy(loading = false, errorMessage = "Unable to load notifications")
            }
        }
    }

    fun markAsRead(notificationId: Int) {
        viewModelScope.launch {
            notificationRepository.markAsRead(notificationId)
        }
    }

    fun markAllAsRead() {
        viewModelScope.launch {
            notificationRepository.markAllAsRead()
        }
    }

    private fun Notification.toNotificationItem() = NotificationItem(
        id = id,
        title = title,
        message = message,
        type = deriveNotificationType(type),
        createdAtDisplay = formatBackendTimestampIST(createdAt),
        isRead = isRead,
        checksheetId = checksheetId
    )
}
