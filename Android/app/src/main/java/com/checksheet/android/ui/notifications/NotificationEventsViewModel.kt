package com.checksheet.android.ui.notifications

import androidx.lifecycle.ViewModel
import com.checksheet.android.data.model.Notification
import com.checksheet.android.domain.repository.NotificationRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.SharedFlow
import javax.inject.Inject

/** Thin Activity-scoped wrapper so MainActivity's app-wide Snackbar (Module 26) can observe
 * NotificationRepository's event stream via hiltViewModel(), consistent with how
 * ThemeModeViewModel/SessionWatcherViewModel expose repository state to the top-level NavHost. */
@HiltViewModel
class NotificationEventsViewModel @Inject constructor(
    notificationRepository: NotificationRepository
) : ViewModel() {
    val newNotificationEvents: SharedFlow<Notification> = notificationRepository.newNotificationEvents
}
