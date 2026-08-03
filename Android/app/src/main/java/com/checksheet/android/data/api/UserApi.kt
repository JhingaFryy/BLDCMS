package com.checksheet.android.data.api

import com.checksheet.android.data.model.PaginatedUsersResponse
import retrofit2.http.GET
import retrofit2.http.Query

interface UserApi {
    @GET("/users/")
    suspend fun getUsers(
        @Query("skip") skip: Int,
        @Query("limit") limit: Int,
        @Query("role") role: String?
    ): PaginatedUsersResponse
}
