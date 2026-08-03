package com.checksheet.android.domain.repository

import com.checksheet.android.data.model.Section

interface SectionRepository {
    suspend fun getSections(): List<Section>
}
