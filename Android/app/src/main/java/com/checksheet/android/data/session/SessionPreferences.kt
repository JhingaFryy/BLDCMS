package com.checksheet.android.data.session

import androidx.datastore.core.DataStore
import androidx.datastore.preferences.core.Preferences
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.stringPreferencesKey
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class SessionPreferences @Inject constructor(
    private val dataStore: DataStore<Preferences>
) {
    private object Keys {
        val accessToken = stringPreferencesKey("access_token")
        val tokenType = stringPreferencesKey("token_type")
    }

    val accessTokenFlow: Flow<String?> = dataStore.data.map { preferences ->
        preferences[Keys.accessToken]
    }

    val tokenTypeFlow: Flow<String?> = dataStore.data.map { preferences ->
        preferences[Keys.tokenType]
    }

    suspend fun saveAccessToken(token: String) {
        dataStore.edit { preferences ->
            preferences[Keys.accessToken] = token
        }
    }

    suspend fun saveTokenType(type: String) {
        dataStore.edit { preferences ->
            preferences[Keys.tokenType] = type
        }
    }

    suspend fun clearSession() {
        dataStore.edit { preferences ->
            preferences.remove(Keys.accessToken)
            preferences.remove(Keys.tokenType)
        }
    }
}
