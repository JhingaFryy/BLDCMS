package com.checksheet.android.data.session

import androidx.datastore.core.DataStore
import androidx.datastore.preferences.core.Preferences
import androidx.datastore.preferences.core.booleanPreferencesKey
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.stringPreferencesKey
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map
import javax.inject.Inject
import javax.inject.Singleton

/** Reuses the same injected DataStore<Preferences> singleton as SessionPreferences (see
 * di/AppModule.kt) - a distinct wrapper class purely to keep app-preference keys separate from
 * session/auth keys, not a second DataStore instance. */
@Singleton
class SettingsPreferences @Inject constructor(
    private val dataStore: DataStore<Preferences>
) {
    private object Keys {
        val themeMode = stringPreferencesKey("theme_mode")
        // Module 44: whether the technician has dismissed the one-time in-app notice explaining
        // what the organization's IT administrators can see/manage on this device.
        val deviceManagementNoticeSeen = booleanPreferencesKey("device_management_notice_seen")
    }

    val themeModeFlow: Flow<String?> = dataStore.data.map { preferences ->
        preferences[Keys.themeMode]
    }

    val deviceManagementNoticeSeenFlow: Flow<Boolean> = dataStore.data.map { preferences ->
        preferences[Keys.deviceManagementNoticeSeen] ?: false
    }

    suspend fun saveThemeMode(mode: String) {
        dataStore.edit { preferences ->
            preferences[Keys.themeMode] = mode
        }
    }

    suspend fun setDeviceManagementNoticeSeen() {
        dataStore.edit { preferences ->
            preferences[Keys.deviceManagementNoticeSeen] = true
        }
    }

    /** Module 44: used by DeviceDataClearer when a CLI-issued CLEAR_APP_DATA command runs -
     * removes every app-preference key this class owns (theme, notice-seen flag, and any future
     * addition), not just the ones known about individually. */
    suspend fun clearAll() {
        dataStore.edit { preferences ->
            preferences.remove(Keys.themeMode)
            preferences.remove(Keys.deviceManagementNoticeSeen)
        }
    }
}
