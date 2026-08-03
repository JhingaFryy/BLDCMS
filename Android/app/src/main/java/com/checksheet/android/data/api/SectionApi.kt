package com.checksheet.android.data.api

import com.checksheet.android.data.model.Section
import retrofit2.http.GET

interface SectionApi {
    @GET("/sections/")
    suspend fun getSections(): List<Section>
}
