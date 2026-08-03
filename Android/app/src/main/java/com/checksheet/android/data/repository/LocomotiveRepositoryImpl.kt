package com.checksheet.android.data.repository

import com.checksheet.android.data.api.LocomotiveApi
import com.checksheet.android.data.model.Locomotive
import com.checksheet.android.domain.repository.LocomotiveRepository
import javax.inject.Inject

class LocomotiveRepositoryImpl @Inject constructor(
    private val locomotiveApi: LocomotiveApi
) : LocomotiveRepository {
    override suspend fun getLocomotives(): List<Locomotive> = locomotiveApi.getLocomotives()

    override suspend fun searchLocomotives(query: String): List<Locomotive> =
        locomotiveApi.searchLocomotives(query)
}
