package com.checksheet.android.ui.history

data class HistoryItem(
    val checksheetId: Int,
    val locomotiveId: Int,
    // Module 36: null for a section with no equipment at all (e.g. M6-HR).
    val equipmentId: Int?,
    val locoNumber: String,
    val equipmentName: String,
    val submittedAtRaw: String?,
    val submittedAtDisplay: String,
    val lifecycleStatus: ChecksheetLifecycleStatus,
    val hasPdf: Boolean
)

/** A selectable id+display-name pair used to populate the Equipment/Section filter chips. */
data class FilterOption(val id: Int, val name: String)

enum class HistorySortOption(val label: String) {
    NEWEST_FIRST("Newest First"),
    OLDEST_FIRST("Oldest First"),
    LOCOMOTIVE_NUMBER("Locomotive Number"),
    EQUIPMENT_NAME("Equipment Name"),
    SUBMISSION_DATE("Submission Date")
}

/**
 * All values are the raw backend query-parameter values (not display labels) except the two date
 * fields, which are kept as epoch millis (UTC midnight) so the UI can drive a DatePicker directly.
 */
data class HistoryFilters(
    val status: String = "",
    val sectionId: Int? = null,
    val equipmentId: Int? = null,
    val locomotiveType: String? = null,
    val technology: String? = null,
    val workType: String? = null,
    val dateFromMillis: Long? = null,
    val dateToMillis: Long? = null
) {
    val isEmpty: Boolean
        get() = status.isBlank() && sectionId == null && equipmentId == null &&
            locomotiveType == null && technology == null && workType == null &&
            dateFromMillis == null && dateToMillis == null
}

data class HistoryUiState(
    val loading: Boolean = true,
    val items: List<HistoryItem> = emptyList(),
    val errorMessage: String? = null,
    val isPdfBusy: Boolean = false,
    val pdfError: String? = null,
    val searchQuery: String = "",
    val filters: HistoryFilters = HistoryFilters(),
    val sortOption: HistorySortOption = HistorySortOption.NEWEST_FIRST,
    val isFilterSheetVisible: Boolean = false,
    val sectionOptions: List<FilterOption> = emptyList(),
    val equipmentOptions: List<FilterOption> = emptyList(),
    val locomotiveTypeOptions: List<String> = emptyList(),
    val technologyOptions: List<String> = emptyList(),
    val scheduleTypeOptions: List<String> = emptyList()
) {
    val hasActiveFilters: Boolean
        get() = searchQuery.isNotBlank() || !filters.isEmpty
}
