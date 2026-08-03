package com.checksheet.android.ui.approvalreview

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.SnackbarHost
import androidx.compose.material3.SnackbarHostState
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.checksheet.android.data.model.ChecksheetDetail
import com.checksheet.android.data.model.ChecksheetFieldValueDetail
import com.checksheet.android.theme.RailwayTheme
import com.checksheet.android.ui.components.AppCard
import com.checksheet.android.ui.components.ErrorState
import com.checksheet.android.ui.components.ShimmerListPlaceholder
import com.checksheet.android.util.formatBackendTimestampIST

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ApprovalReviewScreen(
    viewModel: ApprovalReviewViewModel = hiltViewModel(),
    onNavigateBack: () -> Unit = {},
    onActionComplete: () -> Unit = {}
) {
    val state by viewModel.uiState.collectAsStateWithLifecycle()
    val checksheet = state.checksheet
    val snackbarHostState = remember { SnackbarHostState() }
    var showApproveDialog by remember { mutableStateOf(false) }
    var showRejectDialog by remember { mutableStateOf(false) }
    var rejectReason by remember { mutableStateOf("") }

    LaunchedEffect(state.actionSuccess) {
        val message = state.actionSuccess
        if (message != null) {
            snackbarHostState.showSnackbar(message)
            onActionComplete()
        }
    }

    LaunchedEffect(state.actionError) {
        val message = state.actionError
        if (message != null) {
            snackbarHostState.showSnackbar(message)
            viewModel.onActionErrorShown()
        }
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text(checksheet?.templateName ?: "Review Checksheet") },
                navigationIcon = {
                    IconButton(onClick = onNavigateBack, enabled = !state.isProcessing) {
                        Icon(imageVector = Icons.Filled.ArrowBack, contentDescription = "Back")
                    }
                }
            )
        },
        snackbarHost = { SnackbarHost(snackbarHostState) },
        bottomBar = {
            if (checksheet != null) {
                Surface(shadowElevation = 4.dp) {
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(16.dp),
                        horizontalArrangement = Arrangement.spacedBy(12.dp)
                    ) {
                        OutlinedButton(
                            onClick = { showRejectDialog = true },
                            enabled = !state.isProcessing,
                            modifier = Modifier.weight(1f)
                        ) {
                            Text("Reject")
                        }
                        Button(
                            onClick = { showApproveDialog = true },
                            enabled = !state.isProcessing,
                            modifier = Modifier.weight(1f)
                        ) {
                            if (state.isProcessing) {
                                CircularProgressIndicator(modifier = Modifier.size(18.dp))
                            } else {
                                Text("Approve")
                            }
                        }
                    }
                }
            }
        }
    ) { innerPadding ->
        when {
            state.loading -> {
                Box(modifier = Modifier.fillMaxSize().padding(innerPadding)) {
                    ShimmerListPlaceholder(modifier = Modifier.padding(16.dp))
                }
            }

            state.errorMessage != null && checksheet == null -> {
                ErrorState(
                    message = state.errorMessage ?: "Unable to load checksheet",
                    onRetry = viewModel::retry,
                    modifier = Modifier.fillMaxSize().padding(innerPadding),
                )
            }

            checksheet != null -> {
                LazyColumn(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(innerPadding),
                    contentPadding = PaddingValues(16.dp),
                    verticalArrangement = Arrangement.spacedBy(20.dp)
                ) {
                    item(key = "review-header") {
                        ReviewHeaderCard(checksheet)
                    }

                    item(key = "signature-status") {
                        SignatureStatusCard(
                            status = state.signatureStatus,
                            info = state.signatureInfo,
                            onRefresh = viewModel::refreshSignatureStatus,
                            refreshEnabled = !state.isProcessing
                        )
                    }

                    item(key = "checking-points-title") {
                        Text(text = "Checking Points", style = MaterialTheme.typography.titleMedium)
                    }

                    // GROUP fields are containers with no observation of their own (see Module
                    // 29.5's TemplateField.parent_field_id) - every submitted checksheet still
                    // carries a blank ChecksheetValue row for them, so they're excluded here the
                    // same way pdf_service.generate_checksheet_pdf already excludes them.
                    items(
                        checksheet.values.filter { it.fieldType != "group" }.sortedBy { it.displayOrder },
                        key = { it.fieldId }
                    ) { fieldValue ->
                        // Purpose-built read-only row (not DynamicFieldRenderer, which is the
                        // technician-facing fill-time input registry and is unmodified per this
                        // module's constraints) - shows Standard/Authority/Observation, which
                        // DynamicFieldRenderer's component registry has no slot for at all.
                        CheckingPointCard(fieldValue)
                    }
                }
            }
        }
    }

    if (showApproveDialog) {
        AlertDialog(
            onDismissRequest = { showApproveDialog = false },
            title = { Text("Approve checksheet?") },
            text = { Text("This action cannot be undone.") },
            confirmButton = {
                TextButton(onClick = {
                    showApproveDialog = false
                    viewModel.approve()
                }) {
                    Text("Approve")
                }
            },
            dismissButton = {
                TextButton(onClick = { showApproveDialog = false }) {
                    Text("Cancel")
                }
            }
        )
    }

    if (showRejectDialog) {
        AlertDialog(
            onDismissRequest = { showRejectDialog = false },
            title = { Text("Reject Checksheet") },
            text = {
                Column {
                    Text("Please provide a reason for rejection.")
                    Spacer(modifier = Modifier.height(8.dp))
                    OutlinedTextField(
                        value = rejectReason,
                        onValueChange = { rejectReason = it },
                        label = { Text("Reason") },
                        minLines = 3,
                        modifier = Modifier.fillMaxWidth()
                    )
                }
            },
            confirmButton = {
                TextButton(
                    onClick = {
                        showRejectDialog = false
                        viewModel.reject(rejectReason)
                        rejectReason = ""
                    },
                    enabled = rejectReason.isNotBlank()
                ) {
                    Text("Reject")
                }
            },
            dismissButton = {
                TextButton(onClick = { showRejectDialog = false }) {
                    Text("Cancel")
                }
            }
        )
    }
}

@Composable
private fun ReviewHeaderCard(checksheet: ChecksheetDetail) {
    AppCard(modifier = Modifier.fillMaxWidth()) {
        Column(modifier = Modifier.fillMaxWidth().padding(16.dp)) {
            Text(text = "Checksheet Details", style = MaterialTheme.typography.titleMedium)
            Spacer(modifier = Modifier.height(8.dp))
            HeaderRow(label = "Work Type", value = checksheet.workType?.ifBlank { "-" } ?: "-")
            // Module 32: only ever set for Traction Motor checksheets - shown only when present,
            // rather than cluttering every other equipment's review card with "-" rows.
            checksheet.tractionMotorNumber?.let { HeaderRow(label = "Traction Motor Number", value = it) }
            checksheet.maintenanceType?.let { HeaderRow(label = "Maintenance Type", value = it) }
            HeaderRow(label = "Locomotive Number", value = checksheet.locomotiveNumber ?: "-")
            HeaderRow(label = "Locomotive Type", value = checksheet.locomotiveType ?: "-")
            HeaderRow(label = "Technology", value = checksheet.technology ?: "-")
            HeaderRow(label = "Equipment", value = checksheet.equipmentName ?: "-")
            HeaderRow(label = "Section", value = checksheet.sectionName ?: "-")
            HeaderRow(label = "Technician Name", value = checksheet.technicianName ?: checksheet.technicianMobile)
            HeaderRow(label = "Employee ID", value = checksheet.technicianEmployeeId ?: "-")
            HeaderRow(label = "Status", value = checksheet.status ?: "-")
            HeaderRow(label = "Submitted On", value = formatBackendTimestampIST(checksheet.submittedAt))
        }
    }
}

/**
 * Read-only Sr.No/Checking Point/Standard/Authority/Observation row for the Supervisor Review
 * screen - Standard and Authority come straight from the submitted field's own TemplateField
 * metadata (never generated), matching the checksheet PDF's table exactly.
 */
@Composable
private fun CheckingPointCard(fieldValue: ChecksheetFieldValueDetail) {
    AppCard(modifier = Modifier.fillMaxWidth()) {
        Column(modifier = Modifier.fillMaxWidth().padding(16.dp)) {
            Text(
                text = "${fieldValue.displayOrder}. ${fieldValue.fieldLabel}",
                style = MaterialTheme.typography.titleSmall
            )
            Spacer(modifier = Modifier.height(6.dp))
            fieldValue.standardValue?.takeIf { it.isNotBlank() }?.let {
                HeaderRow(label = "Standard", value = it)
            }
            fieldValue.authorityReference?.takeIf { it.isNotBlank() }?.let {
                HeaderRow(label = "Authority", value = it)
            }
            HeaderRow(label = "Observation", value = fieldValue.fieldValue?.ifBlank { "-" } ?: "-")
        }
    }
}

@Composable
private fun HeaderRow(label: String, value: String, valueColor: Color = Color.Unspecified) {
    Row(modifier = Modifier.fillMaxWidth()) {
        Text(
            text = "$label: ",
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
        Text(text = value, style = MaterialTheme.typography.bodyMedium, color = valueColor)
    }
}

/**
 * Read-only signature status display. Android never signs anything - "Refresh Signature Status"
 * only re-fetches the checksheet (same call the screen already loads with); it cannot trigger signing.
 */
@Composable
private fun SignatureStatusCard(
    status: SignatureStatus,
    info: SignatureInfo?,
    onRefresh: () -> Unit,
    refreshEnabled: Boolean
) {
    // Colors are drawn exclusively from MaterialTheme.colorScheme/RailwayTheme.extendedColors
    // roles (no hardcoded RGB), matching StatusChip's convention: Amber (warning) for an
    // in-progress/pending state, Railway Green (success) for a completed/positive one - keeps
    // this readable (and correctly contrasted) in dark theme too.
    val extended = RailwayTheme.extendedColors
    val (label, color) = when (status) {
        SignatureStatus.PENDING_SIGNATURE -> "Pending" to extended.warning
        SignatureStatus.SIGNED -> "Digitally Signed" to extended.success
        SignatureStatus.REJECTED -> "Rejected" to MaterialTheme.colorScheme.error
        SignatureStatus.UNKNOWN -> "Not Applicable" to MaterialTheme.colorScheme.onSurfaceVariant
    }

    AppCard(modifier = Modifier.fillMaxWidth()) {
        Column(modifier = Modifier.fillMaxWidth().padding(16.dp)) {
            Text(text = "Digital Signature", style = MaterialTheme.typography.titleMedium)
            Spacer(modifier = Modifier.height(8.dp))
            HeaderRow(label = "Status", value = label, valueColor = color)

            if (info != null) {
                Spacer(modifier = Modifier.height(12.dp))
                Text(text = "Signature Information", style = MaterialTheme.typography.titleSmall)
                Spacer(modifier = Modifier.height(4.dp))
                info.signedBy?.let { HeaderRow(label = "Signed By", value = it) }
                info.signatureDate?.let { HeaderRow(label = "Signature Date", value = it) }
                info.certificateName?.let { HeaderRow(label = "Certificate Name", value = it) }
                info.certificateAuthority?.let { HeaderRow(label = "Certificate Authority", value = it) }
            }

            Spacer(modifier = Modifier.height(12.dp))
            OutlinedButton(
                onClick = onRefresh,
                enabled = refreshEnabled,
                modifier = Modifier.fillMaxWidth()
            ) {
                Text("Refresh Signature Status")
            }
        }
    }
}
