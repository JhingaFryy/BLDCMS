package com.checksheet.android.data.api

import com.checksheet.android.data.model.ChecksheetTemplate
import retrofit2.http.GET
import retrofit2.http.Path
import retrofit2.http.Query

interface ChecksheetTemplateApi {
    // section_id (Module 29.5) is optional: omitted, behaves exactly as before; passed, the
    // backend composes that section's common page ahead of this template's own pages.
    @GET("/templates/{templateId}")
    suspend fun getTemplate(
        @Path("templateId") templateId: Int,
        @Query("section_id") sectionId: Int? = null
    ): ChecksheetTemplate

    @GET("/templates/")
    suspend fun getTemplates(): List<ChecksheetTemplate>
}
