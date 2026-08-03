package com.checksheet.android.domain.repository

import kotlinx.coroutines.flow.Flow

interface SessionRepository {
    fun getAccessToken(): Flow<String?>

    suspend fun saveAccessToken(token: String)

    suspend fun saveTokenType(type: String)

    fun getTokenType(): Flow<String?>

    suspend fun clearSession()

    fun hasValidSession(): Flow<Boolean>
}
