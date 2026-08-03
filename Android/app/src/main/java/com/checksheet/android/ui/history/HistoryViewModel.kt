package com.checksheet.android.ui.history

import android.content.ActivityNotFoundException
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.checksheet.android.domain.repository.ChecksheetRepository
import com.checksheet.android.domain.repository.EquipmentRepository
import com.checksheet.android.domain.repository.LocomotiveRepository
import com.checksheet.android.domain.repository.SectionRepository
import com.checksheet.android.util.PdfLauncher
import com.checksheet.android.util.formatBackendTimestamp
import com.checksheet.android.util.mapApiError
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.Job
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import retrofit2.HttpException
import java.io.IOException
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import java.util.TimeZone
import javax.inject.Inject

private const val SEARCH_DEBOUNCE_MS = 300L
private const val MIN_SEARCH_LENGTH = 2
private const val DAY_MILLIS = 24 * 60 * 60 * 1000L

/**
 * Reuses ChecksheetRepository.getChecksheets() (Module 20) - a single generic wrapper around the
 * existing/extended GET /checksheet/ endpoint that also backs getPendingApprovals(). The backend
 * itself restricts a Technician-role caller to their own checksheets, so no new repository method
 * beyond that is needed. Locomotive/equipment/section names now come back directly on each item
 * (Module 20 backend change), so - unlike Module 15's PendingApprovalsViewModel - there is no
 * per-row client-side join against the full master-data lists; those lists are only fetched once
 * to populate the Filter sheet's option chips. PDF viewing reuses the shared PdfLauncher.
 */
@HiltViewModel
class HistoryViewModel @Inject constructor(
    private val checksheetRepository: ChecksheetRepository,
    private val locomotiveRepository: LocomotiveRepository,
    private val sectionRepository: SectionRepository,
    private val equipmentRepository: EquipmentRepository,
    private val pdfLauncher: PdfLauncher
) : ViewModel() {

    private val _uiState = MutableStateFlow(HistoryUiState())
    val uiState: StateFlow<HistoryUiState> = _uiState.asStateFlow()

    private var loadJob: Job? = null
    private var searchJob: Job? = null
    private var pdfJob: Job? = null
    private var lastQuerySignature: String? = null

    init {
        loadFilterOptions()
    }

    fun retry() = refresh(force = true)

    /** Called on every entry to this screen - cheap no-op if the query is unchanged (see [refresh]). */
    fun refresh() = refresh(force = false)

    fun onSearchQueryChanged(query: String) {
        _uiState.value = _uiState.value.copy(searchQuery = query)
        searchJob?.cancel()

        // "Search should begin after 2 characters" - a 1-character query neither clears the list
        // nor fires a request; it simply waits for more input (or for the field to be cleared).
        val trimmed = query.trim()
        if (trimmed.isNotEmpty() && trimmed.length < MIN_SEARCH_LENGTH) return

        searchJob = viewModelScope.launch {
            delay(SEARCH_DEBOUNCE_MS)
            refresh(force = false)
        }
    }

    fun setFilterSheetVisible(visible: Boolean) {
        _uiState.value = _uiState.value.copy(isFilterSheetVisible = visible)
    }

    fun onStatusFilterChanged(status: String) = updateFilters { it.copy(status = status) }

    fun onSectionFilterChanged(sectionId: Int?) = updateFilters { it.copy(sectionId = sectionId) }

    fun onEquipmentFilterChanged(equipmentId: Int?) = updateFilters { it.copy(equipmentId = equipmentId) }

    fun onLocomotiveTypeFilterChanged(locomotiveType: String?) =
        updateFilters { it.copy(locomotiveType = locomotiveType) }

    fun onTechnologyFilterChanged(technology: String?) = updateFilters { it.copy(technology = technology) }

    fun onScheduleTypeFilterChanged(workType: String?) = updateFilters { it.copy(workType = workType) }

    fun onDateFromChanged(millis: Long?) = updateFilters { it.copy(dateFromMillis = millis) }

    fun onDateToChanged(millis: Long?) = updateFilters { it.copy(dateToMillis = millis) }

    fun onSortOptionChanged(option: HistorySortOption) {
        if (option == _uiState.value.sortOption) return
        _uiState.value = _uiState.value.copy(sortOption = option)
        refresh(force = false)
    }

    /** Clears both the search text and every filter, then reloads - used by the empty state's
     * "Clear Filters" action and by the Filter sheet's own clear button. */
    fun clearFilters() {
        searchJob?.cancel()
        _uiState.value = _uiState.value.copy(searchQuery = "", filters = HistoryFilters())
        refresh(force = false)
    }

    private inline fun updateFilters(transform: (HistoryFilters) -> HistoryFilters) {
        _uiState.value = _uiState.value.copy(filters = transform(_uiState.value.filters))
        refresh(force = false)
    }

    private fun refresh(force: Boolean) {
        val state = _uiState.value
        val signature = buildSignature(state)

        // Avoid reloading identical queries - e.g. a configuration change re-entering this screen
        // with the same search/filters/sort already loaded successfully. lastQuerySignature is
        // only set after a successful fetch, so a previously failed load always retries. Pull-to-
        // refresh and Retry pass force = true to always hit the network regardless of signature.
        if (!force && signature == lastQuerySignature) {
            return
        }

        loadJob?.cancel()
        loadJob = viewModelScope.launch {
            _uiState.value = _uiState.value.copy(loading = true, errorMessage = null)

            try {
                val filters = state.filters
                val sortOption = state.sortOption
                val search = effectiveSearch(state.searchQuery)

                val response = checksheetRepository.getChecksheets(
                    skip = 0,
                    limit = 100,
                    search = search,
                    status = filters.status.ifBlank { null },
                    sectionId = filters.sectionId,
                    equipmentId = filters.equipmentId,
                    locomotiveType = filters.locomotiveType,
                    technology = filters.technology,
                    workType = filters.workType,
                    dateFrom = formatDateParam(filters.dateFromMillis, endOfDay = false),
                    dateTo = formatDateParam(filters.dateToMillis, endOfDay = true),
                    sortBy = sortByParam(sortOption),
                    sortOrder = sortOrderParam(sortOption)
                )

                // History tracks the lifecycle of *submitted* checksheets only - drafts are not
                // part of this vocabulary (see ChecksheetLifecycleStatus).
                val checksheets = response.items.filter { it.status?.trim()?.uppercase() != "DRAFT" }

                val items = checksheets.map { summary ->
                    HistoryItem(
                        checksheetId = summary.id,
                        locomotiveId = summary.locomotiveId,
                        equipmentId = summary.equipmentId,
                        locoNumber = summary.locomotiveNumber ?: "-",
                        equipmentName = summary.equipmentName ?: "-",
                        submittedAtRaw = summary.submittedAt ?: summary.createdAt,
                        submittedAtDisplay = formatBackendTimestamp(summary.submittedAt ?: summary.createdAt),
                        lifecycleStatus = deriveLifecycleStatus(summary.status),
                        hasPdf = summary.pdfPath != null
                    )
                }

                val observedWorkTypes = response.items.mapNotNull { it.workType?.trim()?.ifBlank { null } }
                val scheduleTypeOptions = (_uiState.value.scheduleTypeOptions + observedWorkTypes).distinct().sorted()

                lastQuerySignature = signature
                _uiState.value = _uiState.value.copy(
                    loading = false,
                    items = items,
                    scheduleTypeOptions = scheduleTypeOptions
                )
            } catch (e: HttpException) {
                _uiState.value = _uiState.value.copy(loading = false, errorMessage = "Unable to load checksheets")
            } catch (e: IOException) {
                _uiState.value = _uiState.value.copy(loading = false, errorMessage = "Unable to load checksheets")
            } catch (e: Exception) {
                _uiState.value = _uiState.value.copy(loading = false, errorMessage = "Unable to load checksheets")
            }
        }
    }

    /** Best-effort only - populates the Filter sheet's chips. A failure here must never block the
     * main checksheet list, which loads independently via [refresh]. */
    private fun loadFilterOptions() {
        viewModelScope.launch {
            try {
                val sections = sectionRepository.getSections()
                val equipment = equipmentRepository.getEquipment()
                val locomotives = locomotiveRepository.getLocomotives()

                _uiState.value = _uiState.value.copy(
                    sectionOptions = sections.map { FilterOption(it.id, it.name) },
                    equipmentOptions = equipment.map { FilterOption(it.id, it.equipmentName) },
                    locomotiveTypeOptions = locomotives.map { it.locoModel }.distinct().sorted(),
                    technologyOptions = locomotives.map { it.technology }.distinct().sorted()
                )
            } catch (e: Exception) {
                // Silent by design - see kdoc above.
            }
        }
    }

    private fun buildSignature(state: HistoryUiState): String {
        val f = state.filters
        return listOf(
            effectiveSearch(state.searchQuery),
            f.status, f.sectionId, f.equipmentId, f.locomotiveType, f.technology, f.workType,
            f.dateFromMillis, f.dateToMillis, state.sortOption.name
        ).joinToString("|")
    }

    private fun effectiveSearch(raw: String): String? {
        val trimmed = raw.trim()
        return trimmed.takeIf { it.length >= MIN_SEARCH_LENGTH }
    }

    private fun sortByParam(option: HistorySortOption): String = when (option) {
        HistorySortOption.NEWEST_FIRST, HistorySortOption.OLDEST_FIRST -> "created_at"
        HistorySortOption.LOCOMOTIVE_NUMBER -> "loco_number"
        HistorySortOption.EQUIPMENT_NAME -> "equipment_name"
        HistorySortOption.SUBMISSION_DATE -> "submitted_at"
    }

    private fun sortOrderParam(option: HistorySortOption): String = when (option) {
        HistorySortOption.OLDEST_FIRST -> "asc"
        else -> "desc"
    }

    private fun formatDateParam(millis: Long?, endOfDay: Boolean): String? {
        if (millis == null) return null
        val formatter = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss", Locale.US).apply {
            timeZone = TimeZone.getTimeZone("UTC")
        }
        val adjusted = if (endOfDay) millis + (DAY_MILLIS - 1000L) else millis
        return formatter.format(Date(adjusted))
    }

    /** Downloads the PDF only if not already saved locally, then opens it via the OS's own viewer. */
    fun viewPdf(item: HistoryItem) {
        if (!item.hasPdf || _uiState.value.isPdfBusy) return

        pdfJob?.cancel()
        pdfJob = viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isPdfBusy = true, pdfError = null)
            try {
                val file = pdfLauncher.resolveLocalFile(
                    checksheetId = item.checksheetId,
                    locomotiveId = item.locomotiveId,
                    equipmentId = item.equipmentId,
                    submittedAt = item.submittedAtRaw
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

    fun onPdfErrorShown() {
        _uiState.value = _uiState.value.copy(pdfError = null)
    }

    private fun mapPdfHttpError(e: HttpException): String =
        mapApiError(e, overrides = mapOf(404 to "PDF not found."), defaultMessage = "Unable to load PDF.")
}
