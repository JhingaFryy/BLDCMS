package com.checksheet.android.ui.pendingapprovals

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.checksheet.android.domain.repository.ChecksheetRepository
import com.checksheet.android.domain.repository.EquipmentRepository
import com.checksheet.android.domain.repository.LocomotiveRepository
import com.checksheet.android.domain.repository.SectionRepository
import com.checksheet.android.domain.repository.UserRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.Job
import kotlinx.coroutines.async
import kotlinx.coroutines.awaitAll
import kotlinx.coroutines.coroutineScope
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import retrofit2.HttpException
import java.io.IOException
import java.text.SimpleDateFormat
import java.util.Locale
import java.util.TimeZone
import javax.inject.Inject

private const val SEARCH_DEBOUNCE_MS = 300L

@HiltViewModel
class PendingApprovalsViewModel @Inject constructor(
    private val checksheetRepository: ChecksheetRepository,
    private val locomotiveRepository: LocomotiveRepository,
    private val sectionRepository: SectionRepository,
    private val equipmentRepository: EquipmentRepository,
    private val userRepository: UserRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(PendingApprovalsUiState())
    val uiState: StateFlow<PendingApprovalsUiState> = _uiState.asStateFlow()

    private var loadJob: Job? = null
    private var searchJob: Job? = null

    fun onSearchQueryChanged(query: String) {
        _uiState.value = _uiState.value.copy(searchQuery = query)
        searchJob?.cancel()
        searchJob = viewModelScope.launch {
            delay(SEARCH_DEBOUNCE_MS)
            refresh()
        }
    }

    fun onStatusFilterChanged(status: String) {
        if (status == _uiState.value.statusFilter) return
        _uiState.value = _uiState.value.copy(statusFilter = status)
        refresh()
    }

    fun retry() = refresh()

    /** Called on every entry to this screen (including returning from Approval Review) - "refresh
     * automatically" is satisfied by re-loading whenever the screen becomes visible rather than
     * relying on Compose/Navigation composition-lifecycle nuances. */
    fun refresh() {
        loadJob?.cancel()
        loadJob = viewModelScope.launch {
            _uiState.value = _uiState.value.copy(loading = true, errorMessage = null)

            try {
                val query = _uiState.value.searchQuery.trim()
                val statusFilter = _uiState.value.statusFilter

                val items = coroutineScope {
                    val checksheetsDeferred = async {
                        checksheetRepository.getPendingApprovals(
                            search = query.ifBlank { null },
                            status = statusFilter.ifBlank { null }
                        )
                    }
                    val locomotivesDeferred = async { locomotiveRepository.getLocomotives() }
                    val sectionsDeferred = async { sectionRepository.getSections() }
                    val equipmentDeferred = async { equipmentRepository.getEquipment() }
                    val techniciansDeferred = async { userRepository.getTechnicians() }

                    val checksheets = checksheetsDeferred.await()
                    val locomotives = locomotivesDeferred.await().associateBy { it.id }
                    val sections = sectionsDeferred.await().associateBy { it.id }
                    val equipment = equipmentDeferred.await().associateBy { it.id }
                    val technicians = techniciansDeferred.await().associateBy { it.mobile }

                    checksheets.map { summary ->
                        val locomotive = locomotives[summary.locomotiveId]
                        PendingApprovalItem(
                            checksheetId = summary.id,
                            locoNumber = locomotive?.locoNumber ?: "-",
                            locoType = locomotive?.locoModel ?: "-",
                            sectionName = sections[summary.sectionId]?.name ?: "-",
                            // Module 36: summary.equipmentId is null for a section with no
                            // equipment at all (e.g. M6-HR) - falls back to the same "-" placeholder
                            // an unmatched id already used.
                            equipmentName = summary.equipmentId?.let { equipment[it] }?.equipmentName ?: "-",
                            technicianName = technicians[summary.technicianMobile]?.name
                                ?: summary.technicianMobile,
                            submittedAtDisplay = formatDate(summary.submittedAt ?: summary.createdAt),
                            status = summary.status ?: "SUBMITTED"
                        )
                    }
                }

                _uiState.value = _uiState.value.copy(loading = false, items = items)
            } catch (e: HttpException) {
                _uiState.value = _uiState.value.copy(
                    loading = false,
                    errorMessage = "Unable to load pending approvals"
                )
            } catch (e: IOException) {
                _uiState.value = _uiState.value.copy(
                    loading = false,
                    errorMessage = "Unable to load pending approvals"
                )
            } catch (e: Exception) {
                _uiState.value = _uiState.value.copy(
                    loading = false,
                    errorMessage = "Unable to load pending approvals"
                )
            }
        }
    }

    private fun formatDate(raw: String?): String {
        if (raw.isNullOrBlank()) return "-"
        return try {
            val parser = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss", Locale.US)
            parser.timeZone = TimeZone.getTimeZone("UTC")
            val date = parser.parse(raw.substringBefore("."))
            val formatter = SimpleDateFormat("dd MMM yyyy, HH:mm", Locale.US)
            date?.let { formatter.format(it) } ?: raw
        } catch (e: Exception) {
            raw
        }
    }
}
