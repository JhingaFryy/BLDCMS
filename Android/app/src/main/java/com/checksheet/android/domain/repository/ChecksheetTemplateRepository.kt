package com.checksheet.android.domain.repository

import com.checksheet.android.data.model.ChecksheetTemplate

interface ChecksheetTemplateRepository {
    suspend fun getTemplate(templateId: Int, sectionId: Int? = null): ChecksheetTemplate

    suspend fun getTemplates(): List<ChecksheetTemplate>
}
