package com.checksheet.android.data.api

import com.checksheet.android.data.model.Locomotive
import retrofit2.http.GET
import retrofit2.http.Query

interface LocomotiveApi {
    @GET("/locomotives/")
    suspend fun getLocomotives(): List<Locomotive>

    @GET("/locomotives/")
    suspend fun searchLocomotives(@Query("search") search: String): List<Locomotive>
}
