package com.checksheet.android.data.model

import kotlinx.serialization.Serializable

@Serializable
data class ServerStatusResponse(
    val status: String? = null,
    val project: String? = null
)

/** Partial projection of FastAPI's auto-generated /openapi.json - only the one field this app
 * reads (Backend Version). ignoreUnknownKeys discards the rest of the (large) document. */
@Serializable
data class OpenApiDocument(
    val info: OpenApiInfo? = null
)

@Serializable
data class OpenApiInfo(
    val version: String? = null
)
