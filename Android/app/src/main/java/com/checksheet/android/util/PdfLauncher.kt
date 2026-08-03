package com.checksheet.android.util

import android.content.Context
import android.content.Intent
import android.os.Environment
import androidx.core.content.FileProvider
import com.checksheet.android.domain.repository.ChecksheetRepository
import com.checksheet.android.domain.repository.EquipmentRepository
import com.checksheet.android.domain.repository.LocomotiveRepository
import dagger.hilt.android.qualifiers.ApplicationContext
import java.io.File
import java.text.SimpleDateFormat
import java.util.Locale
import java.util.TimeZone
import javax.inject.Inject

/**
 * Shared by HistoryViewModel and ChecksheetDetailViewModel so the download/reuse/open logic for a
 * checksheet's backend-generated PDF exists in exactly one place. Android never generates a PDF -
 * this only fetches the bytes the backend already produced (ChecksheetRepository.downloadChecksheetPdf,
 * reusing the existing GET /checksheet/{id}/pdf/download endpoint) and hands the local file to the
 * OS's own PDF viewer via an ACTION_VIEW intent.
 */
class PdfLauncher @Inject constructor(
    @ApplicationContext private val appContext: Context,
    private val checksheetRepository: ChecksheetRepository,
    private val locomotiveRepository: LocomotiveRepository,
    private val equipmentRepository: EquipmentRepository
) {

    /** Returns the local PDF file, downloading it only if it isn't already present on disk. */
    suspend fun resolveLocalFile(
        checksheetId: Int,
        locomotiveId: Int,
        // Module 36: null for a section with no equipment at all (e.g. M6-HR) - falls back to the
        // "equipment" placeholder in the filename, same as an equipment lookup miss already did.
        equipmentId: Int?,
        submittedAt: String?
    ): File {
        val directory = File(appContext.getExternalFilesDir(Environment.DIRECTORY_DOCUMENTS), "checksheets")
        if (!directory.exists()) {
            directory.mkdirs()
        }

        val file = File(directory, buildFileName(locomotiveId, equipmentId, submittedAt))
        if (!file.exists()) {
            checksheetRepository.downloadChecksheetPdf(checksheetId, file)
        }
        return file
    }

    /** Throws android.content.ActivityNotFoundException if no app can handle a PDF - callers
     * catch that and show "No PDF viewer installed." */
    fun openPdf(file: File) {
        val uri = FileProvider.getUriForFile(appContext, "${appContext.packageName}.fileprovider", file)
        val intent = Intent(Intent.ACTION_VIEW).apply {
            setDataAndType(uri, "application/pdf")
            addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
            addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        }
        appContext.startActivity(intent)
    }

    private suspend fun buildFileName(locomotiveId: Int, equipmentId: Int?, submittedAt: String?): String {
        val locoNumber = locomotiveRepository.getLocomotives()
            .firstOrNull { it.id == locomotiveId }
            ?.locoNumber
            ?: "locomotive"
        val equipmentName = equipmentId
            ?.let { id -> equipmentRepository.getEquipment().firstOrNull { it.id == id } }
            ?.equipmentName
            ?: "equipment"

        return "${sanitize(locoNumber)}_${sanitize(equipmentName)}_${datePart(submittedAt)}.pdf"
    }

    private fun datePart(submittedAt: String?): String {
        if (submittedAt.isNullOrBlank()) return "unknown-date"
        return try {
            val parser = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss", Locale.US)
            parser.timeZone = TimeZone.getTimeZone("UTC")
            val date = parser.parse(submittedAt.substringBefore("."))
            date?.let { SimpleDateFormat("yyyyMMdd", Locale.US).format(it) } ?: "unknown-date"
        } catch (e: Exception) {
            "unknown-date"
        }
    }

    private fun sanitize(value: String): String = value.replace(Regex("[^A-Za-z0-9_-]"), "_")
}
