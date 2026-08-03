package com.checksheet.android.domain.repository

import com.checksheet.android.data.model.Locomotive

interface LocomotiveRepository {
    suspend fun getLocomotives(): List<Locomotive>
    suspend fun searchLocomotives(query: String): List<Locomotive>
}
