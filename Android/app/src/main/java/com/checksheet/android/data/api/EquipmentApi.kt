package com.checksheet.android.data.api

import com.checksheet.android.data.model.Equipment
import retrofit2.http.GET
import retrofit2.http.Query

interface EquipmentApi {
    @GET("/equipment/")
    suspend fun getEquipment(
        @Query("section_id") sectionId: Int? = null,
        @Query("technology") technology: String? = null,
        @Query("locomotive_id") locomotiveId: Int? = null
    ): List<Equipment>
}
