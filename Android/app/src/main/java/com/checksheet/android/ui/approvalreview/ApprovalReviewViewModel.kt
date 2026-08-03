package com.checksheet.android.ui.approvalreview

import androidx.lifecycle.SavedStateHandle
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.checksheet.android.domain.repository.ChecksheetRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.Job
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import retrofit2.HttpException
import java.io.IOException
import javax.inject.Inject

@HiltViewModel
class ApprovalReviewViewModel @Inject constructor(
    private val checksheetRepository: ChecksheetRepository,
    savedStateHandle: SavedStateHandle
) : ViewModel() {

    private val checksheetId: Int? = savedStateHandle.get<String>("checksheetId")?.toIntOrNull()

    private val _uiState = MutableStateFlow(ApprovalReviewUiState())
    val uiState: StateFlow<ApprovalReviewUiState> = _uiState.asStateFlow()

    private var loadJob: Job? = null
    private var actionJob: Job? = null

    init {
        loadChecksheet()
    }

    fun retry() = loadChecksheet()

    /** Re-fetches the checksheet (the only source signature status/info can come from today) -
     * reloads, never signs anything. */
    fun refreshSignatureStatus() = loadChecksheet()

    fun onActionErrorShown() {
        _uiState.value = _uiState.value.copy(actionError = null)
    }

    fun approve() {
        val id = checksheetId
        if (id == null || _uiState.value.isProcessing) return

        actionJob?.cancel()
        actionJob = viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isProcessing = true, actionError = null)

            try {
                checksheetRepository.approveChecksheet(id)
                _uiState.value = _uiState.value.copy(isProcessing = false, actionSuccess = "Approved successfully.")
            } catch (e: HttpException) {
                _uiState.value = _uiState.value.copy(isProcessing = false, actionError = "Unable to approve checksheet.")
            } catch (e: IOException) {
                _uiState.value = _uiState.value.copy(isProcessing = false, actionError = "Unable to approve checksheet.")
            } catch (e: Exception) {
                _uiState.value = _uiState.value.copy(isProcessing = false, actionError = "Unable to approve checksheet.")
            }
        }
    }

    fun reject(reason: String) {
        val id = checksheetId
        if (id == null || _uiState.value.isProcessing) return

        if (reason.isBlank()) {
            _uiState.value = _uiState.value.copy(actionError = "A reason is required to reject.")
            return
        }

        actionJob?.cancel()
        actionJob = viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isProcessing = true, actionError = null)

            try {
                checksheetRepository.rejectChecksheet(id, reason)
                _uiState.value = _uiState.value.copy(isProcessing = false, actionSuccess = "Rejected successfully.")
            } catch (e: HttpException) {
                _uiState.value = _uiState.value.copy(isProcessing = false, actionError = "Unable to reject checksheet.")
            } catch (e: IOException) {
                _uiState.value = _uiState.value.copy(isProcessing = false, actionError = "Unable to reject checksheet.")
            } catch (e: Exception) {
                _uiState.value = _uiState.value.copy(isProcessing = false, actionError = "Unable to reject checksheet.")
            }
        }
    }

    private fun loadChecksheet() {
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
                _uiState.value = _uiState.value.copy(
                    loading = false,
                    checksheet = detail,
                    signatureStatus = deriveSignatureStatus(detail),
                    signatureInfo = deriveSignatureInfo(detail)
                )
            } catch (e: HttpException) {
                _uiState.value = _uiState.value.copy(loading = false, errorMessage = "Unable to load checksheet")
            } catch (e: IOException) {
                _uiState.value = _uiState.value.copy(loading = false, errorMessage = "Unable to load checksheet")
            } catch (e: Exception) {
                _uiState.value = _uiState.value.copy(loading = false, errorMessage = "Unable to load checksheet")
            }
        }
    }
}
