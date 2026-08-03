package com.checksheet.android.data.repository

import com.checksheet.android.data.api.SectionApi
import com.checksheet.android.data.model.Section
import com.checksheet.android.domain.repository.SectionRepository
import javax.inject.Inject

class SectionRepositoryImpl @Inject constructor(
    private val sectionApi: SectionApi
) : SectionRepository {
    override suspend fun getSections(): List<Section> = sectionApi.getSections()
}
