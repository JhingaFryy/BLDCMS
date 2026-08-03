package com.checksheet.android.data.api

import com.checksheet.android.data.model.SectionEquipmentMap
import retrofit2.http.GET

interface SectionEquipmentMapApi {
    @GET("/section-equipment-map/")
    suspend fun getMappings(): List<SectionEquipmentMap>
}
