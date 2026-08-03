package com.checksheet.android.ui.session

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.checksheet.android.domain.repository.SessionRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.stateIn
import javax.inject.Inject

/**
 * Exposes session validity to the top-level NavHost so an expired/invalidated token (cleared by
 * AuthInterceptor on any 401) can bounce the user back to Login from anywhere in the app, not just
 * from screens that happen to check it themselves. Seeded `true` so a fresh cold start doesn't
 * flash a redirect before Splash has had a chance to run its own token check.
 */
@HiltViewModel
class SessionWatcherViewModel @Inject constructor(
    sessionRepository: SessionRepository
) : ViewModel() {
    val hasValidSession: StateFlow<Boolean> = sessionRepository.hasValidSession()
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), true)
}
