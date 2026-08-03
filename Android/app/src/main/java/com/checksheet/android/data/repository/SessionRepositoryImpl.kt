package com.checksheet.android.data.repository

import com.checksheet.android.data.session.SessionPreferences
import com.checksheet.android.domain.repository.SessionRepository
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.combine
import kotlinx.coroutines.flow.map
import javax.inject.Inject

class SessionRepositoryImpl @Inject constructor(
    private val sessionPreferences: SessionPreferences
) : SessionRepository {
    override fun getAccessToken(): Flow<String?> = sessionPreferences.accessTokenFlow

    override suspend fun saveAccessToken(token: String) {
        sessionPreferences.saveAccessToken(token)
    }

    override suspend fun saveTokenType(type: String) {
        sessionPreferences.saveTokenType(type)
    }

    override fun getTokenType(): Flow<String?> = sessionPreferences.tokenTypeFlow

    override suspend fun clearSession() {
        sessionPreferences.clearSession()
    }

    override fun hasValidSession(): Flow<Boolean> = combine(
        sessionPreferences.accessTokenFlow,
        sessionPreferences.tokenTypeFlow
    ) { token, type ->
        !token.isNullOrBlank() && !type.isNullOrBlank()
    }
}
