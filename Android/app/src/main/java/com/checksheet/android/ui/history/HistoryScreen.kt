package com.checksheet.android.ui.history

import com.checksheet.android.ui.components.AppCard
import com.checksheet.android.ui.components.EmptyState
import com.checksheet.android.ui.components.ErrorState
import com.checksheet.android.ui.components.ShimmerListPlaceholder
import com.checksheet.android.ui.components.StatusChip
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.RowScope
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.FilterList
import androidx.compose.material.icons.filled.History
import androidx.compose.material.icons.filled.Search
import androidx.compose.material3.AssistChip
import androidx.compose.material3.Badge
import androidx.compose.material3.BadgedBox
import androidx.compose.material3.Button
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.DatePicker
import androidx.compose.material3.DatePickerDialog
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.FilterChip
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.ModalBottomSheet
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Scaffold
import androidx.compose.material3.SearchBar
import androidx.compose.material3.SnackbarHost
import androidx.compose.material3.SnackbarHostState
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.pulltorefresh.PullToRefreshContainer
import androidx.compose.material3.pulltorefresh.rememberPullToRefreshState
import androidx.compose.material3.rememberDatePickerState
import androidx.compose.material3.rememberModalBottomSheetState
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.input.nestedscroll.nestedScroll
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import java.util.TimeZone

private val STATUS_FILTER_OPTIONS = listOf(
    "" to "All",
    "SUBMITTED" to "Submitted",
    "UNDER_REVIEW" to "Under Review",
    "APPROVED" to "Signed",
    "REJECTED" to "Rejected",
    "NEEDS_CORRECTION" to "Needs Correction"
)

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun HistoryScreen(
    viewModel: HistoryViewModel = hiltViewModel(),
    onNavigateBack: () -> Unit = {},
    onOpenChecksheet: (Int) -> Unit = {}
) {
    val state by viewModel.uiState.collectAsStateWithLifecycle()
    val pullToRefreshState = rememberPullToRefreshState()
    val snackbarHostState = remember { SnackbarHostState() }

    LaunchedEffect(Unit) {
        viewModel.refresh()
    }

    if (pullToRefreshState.isRefreshing) {
        LaunchedEffect(Unit) {
            viewModel.retry()
        }
    }

    LaunchedEffect(state.loading) {
        if (!state.loading) {
            pullToRefreshState.endRefresh()
        }
    }

    LaunchedEffect(state.pdfError) {
        val message = state.pdfError
        if (message != null) {
            snackbarHostState.showSnackbar(message)
            viewModel.onPdfErrorShown()
        }
    }

    Scaffold(
        topBar = {
            Column {
                TopAppBar(
                    title = { Text("Filled Checksheets") },
                    navigationIcon = {
                        IconButton(onClick = onNavigateBack) {
                            Icon(imageVector = Icons.Filled.ArrowBack, contentDescription = "Back")
                        }
                    },
                    actions = {
                        IconButton(onClick = { viewModel.setFilterSheetVisible(true) }) {
                            BadgedBox(badge = { if (state.hasActiveFilters) Badge() }) {
                                Icon(imageVector = Icons.Filled.FilterList, contentDescription = "Filter")
                            }
                        }
                    }
                )
                SearchBar(
                    query = state.searchQuery,
                    onQueryChange = viewModel::onSearchQueryChanged,
                    onSearch = {},
                    active = false,
                    onActiveChange = {},
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(horizontal = 16.dp, vertical = 8.dp),
                    placeholder = { Text("Search by locomotive, equipment or checksheet #") },
                    leadingIcon = { Icon(imageVector = Icons.Filled.Search, contentDescription = null) },
                    trailingIcon = {
                        if (state.searchQuery.isNotEmpty()) {
                            IconButton(onClick = { viewModel.onSearchQueryChanged("") }) {
                                Icon(imageVector = Icons.Filled.Close, contentDescription = "Clear search")
                            }
                        }
                    },
                    content = {}
                )
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .horizontalScroll(rememberScrollState())
                        .padding(horizontal = 16.dp, vertical = 4.dp),
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    HistorySortOption.entries.forEach { option ->
                        FilterChip(
                            selected = state.sortOption == option,
                            onClick = { viewModel.onSortOptionChanged(option) },
                            label = { Text(option.label) }
                        )
                    }
                }
            }
        },
        snackbarHost = { SnackbarHost(snackbarHostState) }
    ) { innerPadding ->
        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
                .nestedScroll(pullToRefreshState.nestedScrollConnection)
        ) {
            when {
                state.loading && state.items.isEmpty() -> {
                    ShimmerListPlaceholder(modifier = Modifier.padding(16.dp))
                }

                state.errorMessage != null && state.items.isEmpty() -> {
                    ErrorState(
                        message = state.errorMessage ?: "Unable to load checksheets",
                        onRetry = viewModel::retry,
                    )
                }

                state.items.isEmpty() -> {
                    EmptyState(
                        message = if (state.hasActiveFilters) {
                            "No matching checksheets found."
                        } else {
                            "No submitted checksheets yet"
                        },
                        icon = Icons.Filled.History,
                        actionLabel = if (state.hasActiveFilters) "Clear Filters" else null,
                        onAction = if (state.hasActiveFilters) viewModel::clearFilters else null,
                    )
                }

                else -> {
                    LazyColumn(
                        modifier = Modifier.fillMaxSize(),
                        contentPadding = PaddingValues(16.dp),
                        verticalArrangement = Arrangement.spacedBy(12.dp)
                    ) {
                        items(state.items, key = { it.checksheetId }) { item ->
                            HistoryRow(
                                item = item,
                                pdfBusy = state.isPdfBusy,
                                onClick = { onOpenChecksheet(item.checksheetId) },
                                onViewPdf = { viewModel.viewPdf(item) }
                            )
                        }
                    }
                }
            }

            PullToRefreshContainer(
                state = pullToRefreshState,
                modifier = Modifier.align(Alignment.TopCenter)
            )
        }
    }

    if (state.isFilterSheetVisible) {
        HistoryFilterSheet(
            state = state,
            onDismiss = { viewModel.setFilterSheetVisible(false) },
            onStatusChanged = viewModel::onStatusFilterChanged,
            onSectionChanged = viewModel::onSectionFilterChanged,
            onEquipmentChanged = viewModel::onEquipmentFilterChanged,
            onLocomotiveTypeChanged = viewModel::onLocomotiveTypeFilterChanged,
            onTechnologyChanged = viewModel::onTechnologyFilterChanged,
            onScheduleTypeChanged = viewModel::onScheduleTypeFilterChanged,
            onDateFromChanged = viewModel::onDateFromChanged,
            onDateToChanged = viewModel::onDateToChanged,
            onClearAll = viewModel::clearFilters
        )
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun HistoryFilterSheet(
    state: HistoryUiState,
    onDismiss: () -> Unit,
    onStatusChanged: (String) -> Unit,
    onSectionChanged: (Int?) -> Unit,
    onEquipmentChanged: (Int?) -> Unit,
    onLocomotiveTypeChanged: (String?) -> Unit,
    onTechnologyChanged: (String?) -> Unit,
    onScheduleTypeChanged: (String?) -> Unit,
    onDateFromChanged: (Long?) -> Unit,
    onDateToChanged: (Long?) -> Unit,
    onClearAll: () -> Unit
) {
    val sheetState = rememberModalBottomSheetState(skipPartiallyExpanded = true)
    var showFromPicker by remember { mutableStateOf(false) }
    var showToPicker by remember { mutableStateOf(false) }
    val filters = state.filters

    ModalBottomSheet(onDismissRequest = onDismiss, sheetState = sheetState) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .verticalScroll(rememberScrollState())
                .padding(horizontal = 20.dp)
                .padding(bottom = 24.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(text = "Filters", style = MaterialTheme.typography.titleLarge)
                TextButton(onClick = onClearAll) { Text("Clear All") }
            }

            FilterSection(title = "Status") {
                STATUS_FILTER_OPTIONS.forEach { (value, label) ->
                    FilterChip(
                        selected = filters.status == value,
                        onClick = { onStatusChanged(value) },
                        label = { Text(label) }
                    )
                }
            }

            FilterSection(title = "Date Range") {
                AssistChip(
                    onClick = { showFromPicker = true },
                    label = { Text(filters.dateFromMillis?.let(::formatDateLabel) ?: "From date") }
                )
                AssistChip(
                    onClick = { showToPicker = true },
                    label = { Text(filters.dateToMillis?.let(::formatDateLabel) ?: "To date") }
                )
                if (filters.dateFromMillis != null || filters.dateToMillis != null) {
                    AssistChip(
                        onClick = {
                            onDateFromChanged(null)
                            onDateToChanged(null)
                        },
                        label = { Text("Clear dates") }
                    )
                }
            }

            if (state.sectionOptions.isNotEmpty()) {
                FilterSection(title = "Section") {
                    FilterChip(
                        selected = filters.sectionId == null,
                        onClick = { onSectionChanged(null) },
                        label = { Text("All") }
                    )
                    state.sectionOptions.forEach { option ->
                        FilterChip(
                            selected = filters.sectionId == option.id,
                            onClick = { onSectionChanged(option.id) },
                            label = { Text(option.name) }
                        )
                    }
                }
            }

            if (state.equipmentOptions.isNotEmpty()) {
                FilterSection(title = "Equipment") {
                    FilterChip(
                        selected = filters.equipmentId == null,
                        onClick = { onEquipmentChanged(null) },
                        label = { Text("All") }
                    )
                    state.equipmentOptions.forEach { option ->
                        FilterChip(
                            selected = filters.equipmentId == option.id,
                            onClick = { onEquipmentChanged(option.id) },
                            label = { Text(option.name) }
                        )
                    }
                }
            }

            if (state.locomotiveTypeOptions.isNotEmpty()) {
                FilterSection(title = "Locomotive Type") {
                    FilterChip(
                        selected = filters.locomotiveType == null,
                        onClick = { onLocomotiveTypeChanged(null) },
                        label = { Text("All") }
                    )
                    state.locomotiveTypeOptions.forEach { type ->
                        FilterChip(
                            selected = filters.locomotiveType == type,
                            onClick = { onLocomotiveTypeChanged(type) },
                            label = { Text(type) }
                        )
                    }
                }
            }

            if (state.technologyOptions.isNotEmpty()) {
                FilterSection(title = "Technology") {
                    FilterChip(
                        selected = filters.technology == null,
                        onClick = { onTechnologyChanged(null) },
                        label = { Text("All") }
                    )
                    state.technologyOptions.forEach { tech ->
                        FilterChip(
                            selected = filters.technology == tech,
                            onClick = { onTechnologyChanged(tech) },
                            label = { Text(tech) }
                        )
                    }
                }
            }

            if (state.scheduleTypeOptions.isNotEmpty()) {
                FilterSection(title = "Schedule Type") {
                    FilterChip(
                        selected = filters.workType == null,
                        onClick = { onScheduleTypeChanged(null) },
                        label = { Text("All") }
                    )
                    state.scheduleTypeOptions.forEach { workType ->
                        FilterChip(
                            selected = filters.workType == workType,
                            onClick = { onScheduleTypeChanged(workType) },
                            label = { Text(workType) }
                        )
                    }
                }
            }

            Button(onClick = onDismiss, modifier = Modifier.fillMaxWidth()) {
                Text("Done")
            }
        }
    }

    if (showFromPicker) {
        HistoryDatePickerDialog(
            initialMillis = filters.dateFromMillis,
            onDismiss = { showFromPicker = false },
            onConfirm = { millis ->
                onDateFromChanged(millis)
                showFromPicker = false
            }
        )
    }
    if (showToPicker) {
        HistoryDatePickerDialog(
            initialMillis = filters.dateToMillis,
            onDismiss = { showToPicker = false },
            onConfirm = { millis ->
                onDateToChanged(millis)
                showToPicker = false
            }
        )
    }
}

@Composable
private fun FilterSection(title: String, content: @Composable RowScope.() -> Unit) {
    Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Text(text = title, style = MaterialTheme.typography.titleSmall)
        Row(
            modifier = Modifier.horizontalScroll(rememberScrollState()),
            horizontalArrangement = Arrangement.spacedBy(8.dp),
            content = content
        )
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun HistoryDatePickerDialog(
    initialMillis: Long?,
    onDismiss: () -> Unit,
    onConfirm: (Long?) -> Unit
) {
    val datePickerState = rememberDatePickerState(initialSelectedDateMillis = initialMillis)
    DatePickerDialog(
        onDismissRequest = onDismiss,
        confirmButton = {
            TextButton(onClick = { onConfirm(datePickerState.selectedDateMillis) }) {
                Text("OK")
            }
        },
        dismissButton = {
            TextButton(onClick = onDismiss) { Text("Cancel") }
        }
    ) {
        DatePicker(state = datePickerState)
    }
}

private fun formatDateLabel(millis: Long): String {
    val formatter = SimpleDateFormat("dd MMM yyyy", Locale.US)
    formatter.timeZone = TimeZone.getTimeZone("UTC")
    return formatter.format(Date(millis))
}

@Composable
private fun HistoryRow(
    item: HistoryItem,
    pdfBusy: Boolean,
    onClick: () -> Unit,
    onViewPdf: () -> Unit
) {
    AppCard(
        onClick = onClick,
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(modifier = Modifier.fillMaxWidth().padding(16.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(text = item.locoNumber, style = MaterialTheme.typography.titleMedium)
            }
            Text(
                text = item.equipmentName,
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
            Text(
                text = item.submittedAtDisplay,
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
            Spacer(modifier = Modifier.height(8.dp))
            StatusChip(status = item.lifecycleStatus)

            if (item.hasPdf) {
                Spacer(modifier = Modifier.height(8.dp))
                OutlinedButton(onClick = onViewPdf, enabled = !pdfBusy) {
                    if (pdfBusy) {
                        com.checksheet.android.ui.components.loading.GeneratingPdfAnimation(size = 18.dp)
                    } else {
                        Text("View PDF")
                    }
                }
            }
        }
    }
}
