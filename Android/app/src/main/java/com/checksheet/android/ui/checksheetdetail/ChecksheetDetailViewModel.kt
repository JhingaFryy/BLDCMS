package com.checksheet.android.ui.checksheetdetail

import android.content.ActivityNotFoundException
import androidx.lifecycle.SavedStateHandle
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.checksheet.android.domain.repository.ChecksheetRepository
import com.checksheet.android.util.PdfLauncher
import com.checksheet.android.util.mapApiError
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.Job
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import retrofit2.HttpException
import java.io.IOException
import javax.inject.Inject

/** Reuses ChecksheetRepository.getChecksheetDetail() (Module 15) as-is - the same GET
 * /checksheet/{id} response already carries everything this screen needs (status, submitted_at,
 * last_modified_at, approved_at, rejection_reason, pdf_path). No new endpoint or repository method
 * was needed for loading; PDF viewing/downloading reuses the shared PdfLauncher (see HistoryViewModel
 * for the other caller), which itself reuses ChecksheetRepository.downloadChecksheetPdf(). */
@HiltViewModel
class ChecksheetDetailViewModel @Inject constructor(
    private val checksheetRepository: ChecksheetRepository,
    private val pdfLauncher: PdfLauncher,
    savedStateHandle: SavedStateHandle
) : ViewModel() {

    private val checksheetId: Int? = savedStateHandle.get<String>("checksheetId")?.toIntOrNull()

    private val _uiState = MutableStateFlow(ChecksheetDetailUiState())
    val uiState: StateFlow<ChecksheetDetailUiState> = _uiState.asStateFlow()

    private var loadJob: Job? = null
    private var pdfJob: Job? = null

    init {
        refresh()
    }

    fun retry() = refresh()

    fun refresh() {
        val id = checksheetId
        if (id == null) {
            _uiState.value = _uiState.value.copy(loading = false, errorMessage = "Checksheet not found")
            return
        }

        loadJob?.cancel()
        loadJob = viewModelScope.launch {
            _uiState.value = _uiState.value.copy(loading = true, errorMessage = null)

            try {
                val detail = checksheetRepository.getChecksheetDetail(id)
                _uiState.value = _uiState.value.copy(loading = false, checksheet = detail)
            } catch (e: HttpException) {
                _uiState.value = _uiState.value.copy(loading = false, errorMessage = "Unable to load checksheet")
            } catch (e: IOException) {
                _uiState.value = _uiState.value.copy(loading = false, errorMessage = "Unable to load checksheet")
            } catch (e: Exception) {
                _uiState.value = _uiState.value.copy(loading = false, errorMessage = "Unable to load checksheet")
            }
        }
    }

    /** Downloads the PDF only if not already saved locally, then opens it via the OS's own viewer. */
    fun viewPdf() {
        val checksheet = _uiState.value.checksheet ?: return
        if (checksheet.pdfPath == null || _uiState.value.isPdfBusy) return

        pdfJob?.cancel()
        pdfJob = viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isPdfBusy = true, pdfError = null)
            try {
                val file = pdfLauncher.resolveLocalFile(
                    checksheetId = checksheet.id,
                    locomotiveId = checksheet.locomotiveId,
                    equipmentId = checksheet.equipmentId,
                    submittedAt = checksheet.submittedAt
                )
                pdfLauncher.openPdf(file)
                _uiState.value = _uiState.value.copy(isPdfBusy = false)
            } catch (e: ActivityNotFoundException) {
                _uiState.value = _uiState.value.copy(isPdfBusy = false, pdfError = "No PDF viewer installed.")
            } catch (e: HttpException) {
                _uiState.value = _uiState.value.copy(isPdfBusy = false, pdfError = mapPdfHttpError(e))
            } catch (e: IOException) {
                _uiState.value = _uiState.value.copy(
                    isPdfBusy = false,
                    pdfError = "Network unavailable. Please try again."
                )
            } catch (e: Exception) {
                _uiState.value = _uiState.value.copy(isPdfBusy = false, pdfError = "Unable to open PDF.")
            }
        }
    }

    /** Downloads the PDF only if not already saved locally. Does not open it. */
    fun downloadPdf() {
        val checksheet = _uiState.value.checksheet ?: return
        if (checksheet.pdfPath == null || _uiState.value.isPdfBusy) return

        pdfJob?.cancel()
        pdfJob = viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isPdfBusy = true, pdfError = null)
            try {
                pdfLauncher.resolveLocalFile(
                    checksheetId = checksheet.id,
                    locomotiveId = checksheet.locomotiveId,
                    equipmentId = checksheet.equipmentId,
                    submittedAt = checksheet.submittedAt
                )
                _uiState.value = _uiState.value.copy(isPdfBusy = false, pdfDownloaded = true)
            } catch (e: HttpException) {
                _uiState.value = _uiState.value.copy(isPdfBusy = false, pdfError = mapPdfHttpError(e))
            } catch (e: IOException) {
                _uiState.value = _uiState.value.copy(
                    isPdfBusy = false,
                    pdfError = "Network unavailable. Please try again."
                )
            } catch (e: Exception) {
                _uiState.value = _uiState.value.copy(isPdfBusy = false, pdfError = "Unable to download PDF.")
            }
        }
    }

    fun onPdfDownloadedMessageShown() {
        _uiState.value = _uiState.value.copy(pdfDownloaded = false)
    }

    fun onPdfErrorShown() {
        _uiState.value = _uiState.value.copy(pdfError = null)
    }

    private fun mapPdfHttpError(e: HttpException): String =
        mapApiError(e, overrides = mapOf(404 to "PDF not found."), defaultMessage = "Unable to load PDF.")
}
