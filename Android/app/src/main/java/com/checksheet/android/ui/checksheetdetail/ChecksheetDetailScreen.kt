package com.checksheet.android.ui.checksheetdetail

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material3.Button
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Scaffold
import androidx.compose.material3.SnackbarHost
import androidx.compose.material3.SnackbarHostState
import androidx.compose.material3.SnackbarResult
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.pulltorefresh.PullToRefreshContainer
import androidx.compose.material3.pulltorefresh.rememberPullToRefreshState
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.input.nestedscroll.nestedScroll
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.checksheet.android.ui.components.ErrorState
import com.checksheet.android.ui.components.ShimmerListPlaceholder
import com.checksheet.android.ui.components.StatusChip
import com.checksheet.android.ui.history.ChecksheetLifecycleStatus
import com.checksheet.android.ui.history.deriveLifecycleStatus
import com.checksheet.android.util.formatBackendTimestamp

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ChecksheetDetailScreen(
    viewModel: ChecksheetDetailViewModel = hiltViewModel(),
    onNavigateBack: () -> Unit = {}
) {
    val state by viewModel.uiState.collectAsStateWithLifecycle()
    val checksheet = state.checksheet
    val pullToRefreshState = rememberPullToRefreshState()
    val snackbarHostState = remember { SnackbarHostState() }

    if (pullToRefreshState.isRefreshing) {
        LaunchedEffect(Unit) {
            viewModel.refresh()
        }
    }

    LaunchedEffect(state.loading) {
        if (!state.loading) {
            pullToRefreshState.endRefresh()
        }
    }

    LaunchedEffect(state.pdfDownloaded) {
        if (state.pdfDownloaded) {
            snackbarHostState.showSnackbar("PDF downloaded successfully.")
            viewModel.onPdfDownloadedMessageShown()
        }
    }

    LaunchedEffect(state.pdfError) {
        val message = state.pdfError
        if (message != null) {
            val result = snackbarHostState.showSnackbar(message = message, actionLabel = "Retry")
            viewModel.onPdfErrorShown()
            if (result == SnackbarResult.ActionPerformed) {
                viewModel.viewPdf()
            }
        }
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text(checksheet?.templateName ?: "Checksheet") },
                navigationIcon = {
                    IconButton(onClick = onNavigateBack) {
                        Icon(imageVector = Icons.Filled.ArrowBack, contentDescription = "Back")
                    }
                }
            )
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
                state.loading && checksheet == null -> {
                    ShimmerListPlaceholder(modifier = Modifier.padding(16.dp), rows = 3)
                }

                state.errorMessage != null && checksheet == null -> {
                    ErrorState(
                        message = state.errorMessage ?: "Unable to load checksheet",
                        onRetry = viewModel::retry,
                    )
                }

                checksheet != null -> {
                    val lifecycleStatus = deriveLifecycleStatus(checksheet.status)

                    Column(
                        modifier = Modifier
                            .fillMaxSize()
                            .verticalScroll(rememberScrollState())
                            .padding(16.dp),
                        verticalArrangement = Arrangement.spacedBy(16.dp)
                    ) {
                        DetailSection(label = "Current Status") {
                            StatusChip(status = lifecycleStatus)
                        }

                        checksheet.submittedAt?.let {
                            DetailRow(label = "Submission Time", value = formatBackendTimestamp(it))
                        }

                        checksheet.lastModifiedAt?.let {
                            DetailRow(label = "Last Updated Time", value = formatBackendTimestamp(it))
                        }

                        if (lifecycleStatus == ChecksheetLifecycleStatus.SIGNED) {
                            checksheet.approvedAt?.let {
                                DetailRow(label = "Digital Signature Time", value = formatBackendTimestamp(it))
                            }
                        }

                        if (lifecycleStatus == ChecksheetLifecycleStatus.REJECTED) {
                            checksheet.rejectionReason?.takeIf { it.isNotBlank() }?.let {
                                DetailRow(label = "Reason for Rejection", value = it)
                            }
                        }

                        // Supervisor Name / Supervisor Remarks / Correction remarks: the backend has
                        // no accessible source for these today for a Technician-role caller
                        // (approved_by/rejected_by are raw user IDs; resolving them requires
                        // GET /users/, which only Supervisor/Admin roles may call). Always hidden,
                        // consistent with "hide fields that are null".

                        if (checksheet.pdfPath != null) {
                            Row(
                                modifier = Modifier.fillMaxWidth(),
                                horizontalArrangement = Arrangement.spacedBy(12.dp)
                            ) {
                                OutlinedButton(
                                    onClick = viewModel::viewPdf,
                                    enabled = !state.isPdfBusy,
                                    modifier = Modifier.weight(1f)
                                ) {
                                    if (state.isPdfBusy) {
                                        com.checksheet.android.ui.components.loading.GeneratingPdfAnimation(size = 18.dp)
                                    } else {
                                        Text("View PDF")
                                    }
                                }
                                Button(
                                    onClick = viewModel::downloadPdf,
                                    enabled = !state.isPdfBusy,
                                    modifier = Modifier.weight(1f)
                                ) {
                                    if (state.isPdfBusy) {
                                        com.checksheet.android.ui.components.loading.GeneratingPdfAnimation(size = 18.dp)
                                    } else {
                                        Text("Download PDF")
                                    }
                                }
                            }
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
}

@Composable
private fun DetailSection(label: String, content: @Composable () -> Unit) {
    Column(modifier = Modifier.fillMaxWidth()) {
        Text(
            text = label,
            style = MaterialTheme.typography.labelMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
        Spacer(modifier = Modifier.height(4.dp))
        content()
    }
}

@Composable
private fun DetailRow(label: String, value: String) {
    Column(modifier = Modifier.fillMaxWidth()) {
        Text(
            text = label,
            style = MaterialTheme.typography.labelMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
        Spacer(modifier = Modifier.height(2.dp))
        Text(text = value, style = MaterialTheme.typography.bodyLarge)
    }
}
