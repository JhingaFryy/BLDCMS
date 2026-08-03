package com.checksheet.android.ui.fillchecksheet

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material3.Button
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.DropdownMenuItem
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.ExposedDropdownMenuBox
import androidx.compose.material3.ExposedDropdownMenuDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.checksheet.android.data.model.Locomotive
import com.checksheet.android.theme.Spacing
import com.checksheet.android.ui.components.AppCard
import com.checksheet.android.ui.components.ErrorState

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun FillChecksheetScreen(
    viewModel: FillChecksheetViewModel = hiltViewModel(),
    onNavigateBack: () -> Unit = {},
    onContinue: (
        locomotiveId: Int,
        sectionId: Int,
        equipmentId: Int?,
        templateId: Int,
        workType: String,
        tractionMotorNumber: String?,
        maintenanceType: String?
    ) -> Unit = { _, _, _, _, _, _, _ -> }
) {
    val state by viewModel.uiState.collectAsStateWithLifecycle()
    val selectedLocomotive = state.selectedLocomotive
    val selectedEquipment = state.selectedEquipment
    val sectionId = state.sectionId
    val resolvedTemplateId = state.resolvedTemplateId
    val workType = state.workType
    var equipmentMenuExpanded by remember { mutableStateOf(false) }
    var workTypeMenuExpanded by remember { mutableStateOf(false) }
    var tmNumberMenuExpanded by remember { mutableStateOf(false) }
    var maintenanceTypeMenuExpanded by remember { mutableStateOf(false) }

    // Module 32: for the overwhelming majority of equipment (requiresMaintenanceTypeSelection ==
    // false) this is trivially satisfied since both values stay null; only equipment with more
    // than one active template (currently only Traction Motor) actually requires them.
    val maintenanceMetadataReady = !state.requiresMaintenanceTypeSelection ||
        (state.tractionMotorNumber != null && state.maintenanceType != null)
    // Module 36: for an equipment-less section (e.g. M6-HR) there is no Equipment to select at
    // all - selectedEquipment stays null forever, so it must not gate readiness the way it does
    // for every other section.
    val equipmentReady = selectedEquipment != null || state.isEquipmentlessSection

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Fill Checksheet") },
                navigationIcon = {
                    IconButton(onClick = onNavigateBack) {
                        Icon(
                            imageVector = Icons.Filled.ArrowBack,
                            contentDescription = "Back"
                        )
                    }
                }
            )
        },
        bottomBar = {
            Surface(shadowElevation = 4.dp) {
                Button(
                    onClick = {
                        if (selectedLocomotive != null &&
                            sectionId != null &&
                            equipmentReady &&
                            resolvedTemplateId != null &&
                            workType != null &&
                            maintenanceMetadataReady
                        ) {
                            onContinue(
                                selectedLocomotive.id,
                                sectionId,
                                selectedEquipment?.id,
                                resolvedTemplateId,
                                workType,
                                state.tractionMotorNumber,
                                state.maintenanceType
                            )
                        }
                    },
                    enabled = selectedLocomotive != null &&
                        sectionId != null &&
                        equipmentReady &&
                        resolvedTemplateId != null &&
                        workType != null &&
                        maintenanceMetadataReady &&
                        !state.isResolvingTemplate,
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(16.dp)
                ) {
                    Text("Continue")
                }
            }
        }
    ) { innerPadding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
                .verticalScroll(rememberScrollState())
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            Column {
                Text(
                    text = "Fill Checksheet",
                    style = MaterialTheme.typography.headlineSmall
                )
                Spacer(modifier = Modifier.height(4.dp))
                Text(
                    text = "Select a work type, locomotive and equipment to begin.",
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }

            // Module 29.8: the technician chooses Work Type here, up front - it is stored with
            // the checksheet on submission and is never editable by the Supervisor afterward.
            ExposedDropdownMenuBox(
                expanded = workTypeMenuExpanded,
                onExpandedChange = { workTypeMenuExpanded = it }
            ) {
                OutlinedTextField(
                    value = workType ?: "",
                    onValueChange = {},
                    readOnly = true,
                    label = { Text("Work Type") },
                    trailingIcon = {
                        ExposedDropdownMenuDefaults.TrailingIcon(expanded = workTypeMenuExpanded)
                    },
                    modifier = Modifier
                        .menuAnchor()
                        .fillMaxWidth()
                )

                ExposedDropdownMenu(
                    expanded = workTypeMenuExpanded,
                    onDismissRequest = { workTypeMenuExpanded = false }
                ) {
                    WORK_TYPE_OPTIONS.forEach { option ->
                        DropdownMenuItem(
                            text = { Text(option) },
                            onClick = {
                                viewModel.onWorkTypeSelected(option)
                                workTypeMenuExpanded = false
                            }
                        )
                    }
                }
            }

            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                OutlinedTextField(
                    value = state.query,
                    onValueChange = viewModel::onQueryChanged,
                    label = { Text("Loco Number") },
                    placeholder = { Text("30245") },
                    singleLine = true,
                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                    modifier = Modifier.fillMaxWidth()
                )

                when {
                    state.isLoading -> {
                        Box(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(vertical = 16.dp),
                            contentAlignment = Alignment.Center
                        ) {
                            CircularProgressIndicator()
                        }
                    }

                    state.errorMessage != null && selectedLocomotive == null -> {
                        ErrorState(
                            message = state.errorMessage ?: "Unable to load locomotives",
                            onRetry = viewModel::retrySearch,
                            modifier = Modifier.fillMaxWidth().height(180.dp),
                        )
                    }

                    state.query.isNotBlank() &&
                        selectedLocomotive == null &&
                        state.locomotives.isEmpty() -> {
                        Text(
                            text = "No locomotives found",
                            style = MaterialTheme.typography.bodyMedium,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }

                    state.locomotives.isNotEmpty() -> {
                        LazyColumn(
                            modifier = Modifier
                                .fillMaxWidth()
                                .heightIn(max = 240.dp),
                            verticalArrangement = Arrangement.spacedBy(8.dp)
                        ) {
                            items(state.locomotives, key = { it.id }) { locomotive ->
                                LocomotiveResultRow(
                                    locomotive = locomotive,
                                    onSelect = { viewModel.onLocomotiveSelected(locomotive) }
                                )
                            }
                        }
                    }

                    selectedLocomotive != null -> {
                        LocomotiveDetailsCard(locomotive = selectedLocomotive)
                    }
                }
            }

            if (selectedLocomotive != null) {
                // Module 36: an equipment-less section (e.g. M6-HR) never shows an Equipment step
                // at all - state.isEquipmentlessSection is set once loadEquipment() completes with
                // zero results for this locomotive's technology (see the ViewModel), the same
                // generic signal the backend uses (a section with no SectionEquipmentMap rows).
                if (!state.isEquipmentlessSection) {
                ExposedDropdownMenuBox(
                    expanded = equipmentMenuExpanded,
                    onExpandedChange = { equipmentMenuExpanded = it }
                ) {
                    OutlinedTextField(
                        value = state.selectedEquipment?.equipmentName ?: "",
                        onValueChange = {},
                        readOnly = true,
                        label = { Text("Equipment") },
                        trailingIcon = {
                            ExposedDropdownMenuDefaults.TrailingIcon(expanded = equipmentMenuExpanded)
                        },
                        modifier = Modifier
                            .menuAnchor()
                            .fillMaxWidth()
                    )

                    ExposedDropdownMenu(
                        expanded = equipmentMenuExpanded,
                        onDismissRequest = { equipmentMenuExpanded = false }
                    ) {
                        if (state.isEquipmentLoading) {
                            DropdownMenuItem(
                                text = { Text("Loading equipment...") },
                                enabled = false,
                                onClick = {}
                            )
                        } else if (state.equipmentList.isEmpty()) {
                            DropdownMenuItem(
                                text = { Text("No equipment available") },
                                enabled = false,
                                onClick = {}
                            )
                        }
                        state.equipmentList.forEach { equipment ->
                            DropdownMenuItem(
                                text = { Text(equipment.equipmentName) },
                                onClick = {
                                    viewModel.onEquipmentSelected(equipment)
                                    equipmentMenuExpanded = false
                                }
                            )
                        }
                    }
                }

                if (!state.isEquipmentLoading && state.equipmentList.isEmpty() && state.errorMessage != null) {
                    Text(
                        text = state.errorMessage ?: "Unable to load equipment",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.error,
                        modifier = Modifier.padding(top = 4.dp)
                    )
                }
                } else if (!state.isEquipmentLoading) {
                    Text(
                        text = "This section has no equipment - continuing directly to the checksheet.",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                        modifier = Modifier.padding(top = 4.dp)
                    )
                }

                // Module 32: only equipment with more than one active template for its technology
                // (currently only Traction Motor) ever shows these - driven entirely by
                // state.requiresMaintenanceTypeSelection, which the ViewModel derives from the
                // actual templates returned by the backend, never a hardcoded equipment check.
                if (equipmentReady && state.requiresMaintenanceTypeSelection) {
                    ExposedDropdownMenuBox(
                        expanded = tmNumberMenuExpanded,
                        onExpandedChange = { tmNumberMenuExpanded = it }
                    ) {
                        OutlinedTextField(
                            value = state.tractionMotorNumber ?: "",
                            onValueChange = {},
                            readOnly = true,
                            label = { Text("Traction Motor Number") },
                            trailingIcon = {
                                ExposedDropdownMenuDefaults.TrailingIcon(expanded = tmNumberMenuExpanded)
                            },
                            modifier = Modifier
                                .menuAnchor()
                                .fillMaxWidth()
                        )

                        ExposedDropdownMenu(
                            expanded = tmNumberMenuExpanded,
                            onDismissRequest = { tmNumberMenuExpanded = false }
                        ) {
                            TRACTION_MOTOR_NUMBER_OPTIONS.forEach { option ->
                                DropdownMenuItem(
                                    text = { Text(option) },
                                    onClick = {
                                        viewModel.onTractionMotorNumberSelected(option)
                                        tmNumberMenuExpanded = false
                                    }
                                )
                            }
                        }
                    }

                    ExposedDropdownMenuBox(
                        expanded = maintenanceTypeMenuExpanded,
                        onExpandedChange = { maintenanceTypeMenuExpanded = it }
                    ) {
                        OutlinedTextField(
                            value = state.maintenanceType ?: "",
                            onValueChange = {},
                            readOnly = true,
                            label = { Text("Maintenance Type") },
                            trailingIcon = {
                                ExposedDropdownMenuDefaults.TrailingIcon(expanded = maintenanceTypeMenuExpanded)
                            },
                            modifier = Modifier
                                .menuAnchor()
                                .fillMaxWidth()
                        )

                        ExposedDropdownMenu(
                            expanded = maintenanceTypeMenuExpanded,
                            onDismissRequest = { maintenanceTypeMenuExpanded = false }
                        ) {
                            state.maintenanceTypeOptions.forEach { option ->
                                DropdownMenuItem(
                                    text = { Text(option) },
                                    onClick = {
                                        viewModel.onMaintenanceTypeSelected(option)
                                        maintenanceTypeMenuExpanded = false
                                    }
                                )
                            }
                        }
                    }
                }

                if (equipmentReady) {
                    when {
                        state.isResolvingTemplate -> {
                            com.checksheet.android.ui.components.loading.LoadingChecksheetAnimation(
                                modifier = Modifier.padding(top = 8.dp),
                            )
                        }

                        state.templateError != null -> {
                            Column(modifier = Modifier.padding(top = 8.dp)) {
                                Text(
                                    text = state.templateError ?: "Unable to load checksheet template",
                                    style = MaterialTheme.typography.bodySmall,
                                    color = MaterialTheme.colorScheme.error
                                )
                                Spacer(modifier = Modifier.height(4.dp))
                                Button(onClick = viewModel::retryTemplateResolution) {
                                    Text("Retry")
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}

@Composable
private fun LocomotiveDetailsCard(locomotive: Locomotive) {
    AppCard(modifier = Modifier.fillMaxWidth()) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp)
        ) {
            Text(
                text = "Locomotive Details",
                style = MaterialTheme.typography.titleMedium
            )
            Spacer(modifier = Modifier.height(8.dp))
            LocomotiveDetailRow(label = "Number", value = locomotive.locoNumber)
            LocomotiveDetailRow(label = "Type", value = locomotive.locoModel)
            LocomotiveDetailRow(label = "Technology", value = humanizeTechnology(locomotive.technology))
        }
    }
}

@Composable
private fun LocomotiveDetailRow(label: String, value: String) {
    Row(modifier = Modifier.fillMaxWidth()) {
        Text(
            text = "$label : ",
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
        Text(
            text = value,
            style = MaterialTheme.typography.bodyMedium
        )
    }
}

private fun humanizeTechnology(rawTechnology: String): String =
    rawTechnology
        .split("_")
        .filter { it.isNotBlank() }
        .joinToString(" ") { part -> part.lowercase().replaceFirstChar { c -> c.uppercase() } }

@Composable
private fun LocomotiveResultRow(
    locomotive: Locomotive,
    onSelect: () -> Unit
) {
    AppCard(
        onClick = onSelect,
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp)
        ) {
            Text(
                text = locomotive.locoNumber,
                style = MaterialTheme.typography.titleMedium
            )
            Text(
                text = locomotive.locoModel,
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
    }
}
