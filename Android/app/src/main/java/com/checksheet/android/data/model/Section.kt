package com.checksheet.android.data.model

import kotlinx.serialization.Serializable

@Serializable
data class Section(
    val id: Int,
    val name: String
)
