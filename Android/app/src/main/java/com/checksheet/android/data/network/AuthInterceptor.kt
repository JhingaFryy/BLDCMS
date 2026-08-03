package com.checksheet.android.data.network

import com.checksheet.android.domain.repository.SessionRepository
import kotlinx.coroutines.flow.firstOrNull
import kotlinx.coroutines.runBlocking
import okhttp3.Interceptor
import okhttp3.Response
import javax.inject.Inject

class AuthInterceptor @Inject constructor(
    private val sessionRepository: SessionRepository
) : Interceptor {
    override fun intercept(chain: Interceptor.Chain): Response {
        val request = chain.request()
        val token = runBlocking { sessionRepository.getAccessToken().firstOrNull() }

        val authenticatedRequest = if (token.isNullOrBlank()) {
            request
        } else {
            request.newBuilder()
                .addHeader("Authorization", "Bearer $token")
                .build()
        }

        val response = chain.proceed(authenticatedRequest)

        // A 401 on a request that carried a token means that token is no longer valid (expired or
        // revoked server-side) - clear it so the app doesn't keep retrying with a dead session.
        // Login/OTP requests never carry a token, so a bad-credentials 401 there is unaffected.
        if (response.code == 401 && !token.isNullOrBlank()) {
            runBlocking { sessionRepository.clearSession() }
        }

        return response
    }
}
