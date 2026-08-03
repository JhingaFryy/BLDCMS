package com.checksheet.android.ui.settings

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.checksheet.android.data.session.SettingsPreferences
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.map
import kotlinx.coroutines.flow.stateIn
import javax.inject.Inject

/** Activity-scoped (read by ChecksheetTheme, which wraps the whole app, outside of any nav
 * back-stack entry) - not the same ViewModel instance as SettingsScreen's, but both observe the
 * same underlying DataStore-backed Flow, so a change made in Settings is reflected here (and thus
 * app-wide) as soon as it's saved, with no extra plumbing needed. */
@HiltViewModel
class ThemeModeViewModel @Inject constructor(
    settingsPreferences: SettingsPreferences
) : ViewModel() {
    val themeMode: StateFlow<ThemeMode> = settingsPreferences.themeModeFlow
        .map { parseThemeMode(it) }
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), ThemeMode.SYSTEM)
}
