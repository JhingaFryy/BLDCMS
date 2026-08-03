package com.checksheet.android.data.model

import kotlinx.serialization.json.Json
import org.junit.Assert.assertEquals
import org.junit.Test

class LoginResponseSerializationTest {
    @Test
    fun serializesBackendLoginResponseShape() {
        val json = """
            {
              "requires_otp": true,
              "message": "OTP sent"
            }
        """.trimIndent()

        val model = Json.decodeFromString<LoginResponse>(json)

        assertEquals(true, model.requiresOtp)
        assertEquals("OTP sent", model.message)
    }
}
