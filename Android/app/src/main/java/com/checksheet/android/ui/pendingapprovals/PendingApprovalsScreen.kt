package com.checksheet.android.ui.pendingapprovals

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.AssignmentTurnedIn
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.FilterChip
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.checksheet.android.ui.components.AppCard
import com.checksheet.android.ui.components.EmptyState
import com.checksheet.android.ui.components.ErrorState
import com.checksheet.android.ui.components.ShimmerListPlaceholder

private val STATUS_FILTERS = listOf(
    "SUBMITTED" to "Submitted",
    "APPROVED" to "Approved",
    "REJECTED" to "Rejected",
    "" to "All"
)

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun PendingApprovalsScreen(
    viewModel: PendingApprovalsViewModel = hiltViewModel(),
    onNavigateBack: () -> Unit = {},
    onOpenChecksheet: (Int) -> Unit = {}
) {
    val state by viewModel.uiState.collectAsStateWithLifecycle()
    val listState = rememberLazyListState()

    LaunchedEffect(Unit) {
        viewModel.refresh()
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Pending Approvals") },
                navigationIcon = {
                    IconButton(onClick = onNavigateBack) {
                        Icon(imageVector = Icons.Filled.ArrowBack, contentDescription = "Back")
                    }
                }
            )
        }
    ) { innerPadding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            OutlinedTextField(
                value = state.searchQuery,
                onValueChange = viewModel::onSearchQueryChanged,
                label = { Text("Search") },
                singleLine = true,
                modifier = Modifier.fillMaxWidth()
            )

            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                STATUS_FILTERS.forEach { (value, label) ->
                    FilterChip(
                        selected = state.statusFilter == value,
                        onClick = { viewModel.onStatusFilterChanged(value) },
                        label = { Text(label) }
                    )
                }
            }

            when {
                state.loading -> {
                    ShimmerListPlaceholder()
                }

                state.errorMessage != null -> {
                    ErrorState(
                        message = state.errorMessage ?: "Unable to load pending approvals",
                        onRetry = viewModel::retry,
                    )
                }

                state.items.isEmpty() -> {
                    EmptyState(
                        message = "No checksheets found",
                        icon = Icons.Filled.AssignmentTurnedIn,
                    )
                }

                else -> {
                    LazyColumn(
                        state = listState,
                        verticalArrangement = Arrangement.spacedBy(12.dp),
                        modifier = Modifier.fillMaxSize()
                    ) {
                        items(state.items, key = { it.checksheetId }) { item ->
                            PendingApprovalCard(
                                item = item,
                                onClick = { onOpenChecksheet(item.checksheetId) }
                            )
                        }
                    }
                }
            }
        }
    }
}

@Composable
private fun PendingApprovalCard(item: PendingApprovalItem, onClick: () -> Unit) {
    AppCard(
        onClick = onClick,
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(modifier = Modifier.fillMaxWidth().padding(16.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Text(text = item.locoNumber, style = MaterialTheme.typography.titleMedium)
                Text(
                    text = item.status,
                    style = MaterialTheme.typography.labelMedium,
                    color = MaterialTheme.colorScheme.primary
                )
            }
            Text(
                text = item.locoType,
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
            Spacer(modifier = Modifier.height(8.dp))
            InfoRow(label = "Section", value = item.sectionName)
            InfoRow(label = "Equipment", value = item.equipmentName)
            InfoRow(label = "Technician", value = item.technicianName)
            InfoRow(label = "Submitted", value = item.submittedAtDisplay)
        }
    }
}

@Composable
private fun InfoRow(label: String, value: String) {
    Row(modifier = Modifier.fillMaxWidth()) {
        Text(
            text = "$label: ",
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
        Text(
            text = value,
            style = MaterialTheme.typography.bodySmall
        )
    }
}
