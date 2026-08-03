package com.checksheet.android.domain.repository

import com.checksheet.android.data.model.ChecksheetDetail
import com.checksheet.android.data.model.ChecksheetFieldValue
import com.checksheet.android.data.model.ChecksheetHeaderResponse
import com.checksheet.android.data.model.ChecksheetSummary
import com.checksheet.android.data.model.PaginatedChecksheetResponse
import java.io.File

interface ChecksheetRepository {
    /**
     * Creates or updates the checksheet header with the current form values. There is no user-facing
     * "save as draft" action anywhere in the app - this is called internally, immediately followed by
     * [submitChecksheet], only to obtain a header id when one doesn't exist yet. Pass the
     * previously-returned [checksheetId] on every call after the first so the same row is updated in
     * place instead of creating duplicates.
     */
    suspend fun saveDraft(
        checksheetId: Int?,
        locomotiveId: Int,
        sectionId: Int,
        // Module 36: null for a section with no equipment at all (e.g. M6-HR).
        equipmentId: Int?,
        templateId: Int,
        workType: String,
        // Module 32: null for every equipment other than Traction Motor.
        tractionMotorNumber: String? = null,
        maintenanceType: String? = null,
        values: List<ChecksheetFieldValue>
    ): ChecksheetHeaderResponse

    /**
     * Ensures the header's work_type is set (the backend rejects submission of a blank work_type),
     * then transitions the checksheet to SUBMITTED via the existing status endpoint.
     */
    suspend fun submitChecksheet(checksheetId: Int, workType: String): ChecksheetHeaderResponse

    /** Reuses the existing GET /checksheet/ list endpoint - "newest first" via sort_order=desc. */
    suspend fun getPendingApprovals(search: String?, status: String?): List<ChecksheetSummary>

    /**
     * Full-parameter access to the same GET /checksheet/ list endpoint used by
     * [getPendingApprovals] (which now delegates to this, so there is a single call site for the
     * Retrofit method). Used by Module 20's History search/filter/sort - all params are optional
     * and map 1:1 onto backend query parameters that already exist or were added for this module.
     */
    suspend fun getChecksheets(
        skip: Int = 0,
        limit: Int = 100,
        search: String? = null,
        status: String? = null,
        sectionId: Int? = null,
        equipmentId: Int? = null,
        locomotiveId: Int? = null,
        locomotiveType: String? = null,
        technology: String? = null,
        workType: String? = null,
        dateFrom: String? = null,
        dateTo: String? = null,
        sortBy: String? = null,
        sortOrder: String = "desc"
    ): PaginatedChecksheetResponse

    suspend fun getChecksheetDetail(checksheetId: Int): ChecksheetDetail

    /**
     * The backend's status state machine only allows SUBMITTED -> UNDER_REVIEW -> APPROVED/REJECTED
     * (a direct SUBMITTED -> APPROVED/REJECTED call is rejected with 400). "Under review" is not a
     * user-facing concept anywhere in this module's spec, so both transitions are sent back-to-back
     * here, invisibly to the caller.
     */
    suspend fun approveChecksheet(checksheetId: Int)

    suspend fun rejectChecksheet(checksheetId: Int, reason: String)

    /** Reuses the existing GET /checksheet/{id}/pdf/download endpoint - streams the response
     * straight to [destination] rather than loading the whole PDF into memory. */
    suspend fun downloadChecksheetPdf(checksheetId: Int, destination: File)
}
