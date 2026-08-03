package com.checksheet.android.data.repository

import com.checksheet.android.data.api.ChecksheetTemplateApi
import com.checksheet.android.data.model.ChecksheetTemplate
import com.checksheet.android.domain.repository.ChecksheetTemplateRepository
import javax.inject.Inject

class ChecksheetTemplateRepositoryImpl @Inject constructor(
    private val checksheetTemplateApi: ChecksheetTemplateApi
) : ChecksheetTemplateRepository {
    override suspend fun getTemplate(templateId: Int, sectionId: Int?): ChecksheetTemplate =
        checksheetTemplateApi.getTemplate(templateId, sectionId)

    override suspend fun getTemplates(): List<ChecksheetTemplate> =
        checksheetTemplateApi.getTemplates()
}
