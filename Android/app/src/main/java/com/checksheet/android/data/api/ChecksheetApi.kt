package com.checksheet.android.data.api

import com.checksheet.android.data.model.ChecksheetDetail
import com.checksheet.android.data.model.ChecksheetHeaderCreateRequest
import com.checksheet.android.data.model.ChecksheetHeaderResponse
import com.checksheet.android.data.model.ChecksheetHeaderUpdateRequest
import com.checksheet.android.data.model.ChecksheetStatusUpdateRequest
import com.checksheet.android.data.model.PaginatedChecksheetResponse
import okhttp3.ResponseBody
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.PATCH
import retrofit2.http.PUT
import retrofit2.http.POST
import retrofit2.http.Path
import retrofit2.http.Query
import retrofit2.http.Streaming

interface ChecksheetApi {
    @POST("/checksheet/")
    suspend fun createChecksheet(@Body request: ChecksheetHeaderCreateRequest): ChecksheetHeaderResponse

    @PUT("/checksheet/{checksheetId}")
    suspend fun updateChecksheet(
        @Path("checksheetId") checksheetId: Int,
        @Body request: ChecksheetHeaderUpdateRequest
    ): ChecksheetHeaderResponse

    @PATCH("/checksheet/{checksheetId}/status")
    suspend fun updateStatus(
        @Path("checksheetId") checksheetId: Int,
        @Body request: ChecksheetStatusUpdateRequest
    ): ChecksheetHeaderResponse

    @GET("/checksheet/")
    suspend fun getChecksheets(
        @Query("skip") skip: Int,
        @Query("limit") limit: Int,
        @Query("search") search: String?,
        @Query("status") status: String?,
        @Query("section_id") sectionId: Int? = null,
        @Query("equipment_id") equipmentId: Int? = null,
        @Query("locomotive_id") locomotiveId: Int? = null,
        @Query("locomotive_type") locomotiveType: String? = null,
        @Query("technology") technology: String? = null,
        @Query("work_type") workType: String? = null,
        @Query("date_from") dateFrom: String? = null,
        @Query("date_to") dateTo: String? = null,
        @Query("sort_by") sortBy: String? = null,
        @Query("sort_order") sortOrder: String
    ): PaginatedChecksheetResponse

    @GET("/checksheet/{checksheetId}")
    suspend fun getChecksheetDetail(@Path("checksheetId") checksheetId: Int): ChecksheetDetail

    @Streaming
    @GET("/checksheet/{checksheetId}/pdf/download")
    suspend fun downloadChecksheetPdf(@Path("checksheetId") checksheetId: Int): Response<ResponseBody>
}
