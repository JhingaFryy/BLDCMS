package com.checksheet.android.data.repository

import com.checksheet.android.data.api.ChecksheetApi
import com.checksheet.android.data.model.ChecksheetDetail
import com.checksheet.android.data.model.ChecksheetFieldValue
import com.checksheet.android.data.model.ChecksheetHeaderCreateRequest
import com.checksheet.android.data.model.ChecksheetHeaderResponse
import com.checksheet.android.data.model.ChecksheetHeaderUpdateRequest
import com.checksheet.android.data.model.ChecksheetStatusUpdateRequest
import com.checksheet.android.data.model.ChecksheetSummary
import com.checksheet.android.data.model.PaginatedChecksheetResponse
import com.checksheet.android.domain.repository.ChecksheetRepository
import retrofit2.HttpException
import java.io.File
import java.io.IOException
import javax.inject.Inject

class ChecksheetRepositoryImpl @Inject constructor(
    private val checksheetApi: ChecksheetApi
) : ChecksheetRepository {

    override suspend fun saveDraft(
        checksheetId: Int?,
        locomotiveId: Int,
        sectionId: Int,
        equipmentId: Int?,
        templateId: Int,
        workType: String,
        tractionMotorNumber: String?,
        maintenanceType: String?,
        values: List<ChecksheetFieldValue>
    ): ChecksheetHeaderResponse {
        return if (checksheetId == null) {
            checksheetApi.createChecksheet(
                ChecksheetHeaderCreateRequest(
                    locomotiveId = locomotiveId,
                    sectionId = sectionId,
                    equipmentId = equipmentId,
                    templateId = templateId,
                    workType = workType,
                    tractionMotorNumber = tractionMotorNumber,
                    maintenanceType = maintenanceType,
                    status = "DRAFT",
                    values = values
                )
            )
        } else {
            checksheetApi.updateChecksheet(
                checksheetId = checksheetId,
                request = ChecksheetHeaderUpdateRequest(values = values)
            )
        }
    }

    override suspend fun submitChecksheet(checksheetId: Int, workType: String): ChecksheetHeaderResponse {
        checksheetApi.updateChecksheet(
            checksheetId = checksheetId,
            request = ChecksheetHeaderUpdateRequest(workType = workType)
        )
        return checksheetApi.updateStatus(
            checksheetId = checksheetId,
            request = ChecksheetStatusUpdateRequest(status = "SUBMITTED")
        )
    }

    override suspend fun getPendingApprovals(search: String?, status: String?): List<ChecksheetSummary> =
        getChecksheets(search = search, status = status).items

    override suspend fun getChecksheets(
        skip: Int,
        limit: Int,
        search: String?,
        status: String?,
        sectionId: Int?,
        equipmentId: Int?,
        locomotiveId: Int?,
        locomotiveType: String?,
        technology: String?,
        workType: String?,
        dateFrom: String?,
        dateTo: String?,
        sortBy: String?,
        sortOrder: String
    ): PaginatedChecksheetResponse =
        checksheetApi.getChecksheets(
            skip = skip,
            limit = limit,
            search = search,
            status = status,
            sectionId = sectionId,
            equipmentId = equipmentId,
            locomotiveId = locomotiveId,
            locomotiveType = locomotiveType,
            technology = technology,
            workType = workType,
            dateFrom = dateFrom,
            dateTo = dateTo,
            sortBy = sortBy,
            sortOrder = sortOrder
        )

    override suspend fun getChecksheetDetail(checksheetId: Int): ChecksheetDetail =
        checksheetApi.getChecksheetDetail(checksheetId)

    override suspend fun approveChecksheet(checksheetId: Int) {
        checksheetApi.updateStatus(checksheetId, ChecksheetStatusUpdateRequest(status = "UNDER_REVIEW"))
        checksheetApi.updateStatus(checksheetId, ChecksheetStatusUpdateRequest(status = "APPROVED"))
    }

    override suspend fun rejectChecksheet(checksheetId: Int, reason: String) {
        checksheetApi.updateStatus(checksheetId, ChecksheetStatusUpdateRequest(status = "UNDER_REVIEW"))
        checksheetApi.updateStatus(
            checksheetId,
            ChecksheetStatusUpdateRequest(status = "REJECTED", rejectionReason = reason)
        )
    }

    override suspend fun downloadChecksheetPdf(checksheetId: Int, destination: File) {
        val response = checksheetApi.downloadChecksheetPdf(checksheetId)
        if (!response.isSuccessful) {
            throw HttpException(response)
        }
        val body = response.body() ?: throw IOException("Empty PDF response")

        destination.parentFile?.mkdirs()
        body.byteStream().use { input ->
            destination.outputStream().use { output ->
                input.copyTo(output)
            }
        }
    }
}
