package com.checksheet.android.ui.checksheet

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
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
import androidx.compose.foundation.border
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Scaffold
import androidx.compose.material3.SnackbarHost
import androidx.compose.material3.SnackbarHostState
import androidx.compose.material3.SnackbarResult
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.checksheet.android.renderer.DynamicFieldRenderer
import com.checksheet.android.renderer.FieldType
import com.checksheet.android.renderer.components.GroupComponent
import com.checksheet.android.theme.Spacing
import com.checksheet.android.ui.components.AppCard
import com.checksheet.android.ui.components.ErrorState
import com.checksheet.android.ui.components.ShimmerListPlaceholder
import kotlinx.coroutines.launch

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ChecksheetScreen(
    viewModel: ChecksheetViewModel = hiltViewModel(),
    onNavigateBack: () -> Unit = {},
    onSubmitSuccess: () -> Unit = {}
) {
    val state by viewModel.uiState.collectAsStateWithLifecycle()
    val template = state.template
    val formState = state.formState
    val snackbarHostState = remember { SnackbarHostState() }
    val listState = rememberLazyListState()
    val coroutineScope = rememberCoroutineScope()
    var showSubmitConfirmDialog by remember { mutableStateOf(false) }

    val busy = state.isSubmitting
    val isLastPage = state.currentPage >= state.totalPages
    // Module 29.5: multi-page templates - only this page's top-level fields are shown; grouped
    // fields' children render recursively inside their parent's GroupComponent, not as separate items.
    val currentPageFields = remember(template, state.currentPage) {
        template?.fields
            ?.filter { it.pageNumber == state.currentPage && it.parentFieldId == null }
            ?.sortedBy { it.displayOrder }
            ?: emptyList()
    }

    LaunchedEffect(state.currentPage) {
        listState.scrollToItem(0)
    }

    LaunchedEffect(state.submitSuccess) {
        if (state.submitSuccess) {
            snackbarHostState.showSnackbar("Checksheet submitted successfully.")
            onSubmitSuccess()
        }
    }

    LaunchedEffect(state.submitError) {
        val message = state.submitError
        if (message != null) {
            val result = snackbarHostState.showSnackbar(
                message = message,
                actionLabel = "Retry"
            )
            viewModel.onSubmitErrorMessageShown()
            if (result == SnackbarResult.ActionPerformed) {
                viewModel.submitChecksheet()
            }
        }
    }

    Scaffold(
        topBar = {
            Column {
                TopAppBar(
                    title = {
                        Column {
                            Text(template?.templateName ?: "Checksheet")
                            if (template != null && state.totalPages > 1) {
                                Text(
                                    text = "Page ${state.currentPage} of ${state.totalPages}",
                                    style = MaterialTheme.typography.bodySmall
                                )
                            }
                        }
                    },
                    navigationIcon = {
                        IconButton(onClick = onNavigateBack, enabled = !busy) {
                            Icon(imageVector = Icons.Filled.ArrowBack, contentDescription = "Back")
                        }
                    }
                )
                // Module 31: a sticky progress indicator - part of the TopAppBar column, so it never
                // scrolls away with the page's content, giving a persistent sense of how far along
                // a multi-page checksheet the technician is.
                if (template != null && state.totalPages > 1) {
                    com.checksheet.android.ui.components.cinematic.ProgressTimeline(
                        currentPage = state.currentPage,
                        totalPages = state.totalPages,
                        modifier = Modifier.fillMaxWidth(),
                    )
                }
            }
        },
        snackbarHost = { SnackbarHost(snackbarHostState) },
        bottomBar = {
            Surface(shadowElevation = 4.dp) {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(Spacing.md),
                    horizontalArrangement = Arrangement.spacedBy(Spacing.sm)
                ) {
                    OutlinedButton(
                        onClick = {
                            if (state.currentPage > 1) {
                                viewModel.previousPage()
                            } else {
                                onNavigateBack()
                            }
                        },
                        enabled = !busy && !state.submitSuccess,
                        shape = MaterialTheme.shapes.medium,
                        modifier = Modifier.weight(1f).height(48.dp)
                    ) {
                        Text("Previous")
                    }
                    Button(
                        onClick = {
                            if (!isLastPage) {
                                viewModel.nextPage()
                                return@Button
                            }

                            if (viewModel.validateForSubmit()) {
                                showSubmitConfirmDialog = true
                            } else {
                                coroutineScope.launch {
                                    snackbarHostState.showSnackbar("Please complete all mandatory fields.")
                                }
                                val firstInvalidField = template?.fields?.firstOrNull { it.id in formState.errors }
                                if (firstInvalidField != null) {
                                    if (firstInvalidField.pageNumber != state.currentPage) {
                                        viewModel.goToPage(firstInvalidField.pageNumber)
                                    } else {
                                        val idx = currentPageFields.indexOfFirst { it.id == firstInvalidField.id }
                                        if (idx >= 0) {
                                            coroutineScope.launch {
                                                listState.animateScrollToItem(idx)
                                            }
                                        }
                                    }
                                }
                            }
                        },
                        enabled = template != null && !busy && !state.submitSuccess,
                        shape = MaterialTheme.shapes.medium,
                        modifier = Modifier.weight(1f).height(48.dp)
                    ) {
                        if (state.isSubmitting) {
                            com.checksheet.android.ui.components.loading.SavingSignalAnimation(inProgress = true, size = 18.dp)
                        } else {
                            Text(if (isLastPage) "Submit" else "Next")
                        }
                    }
                }
            }
        }
    ) { innerPadding ->
        when {
            state.loading -> {
                Box(modifier = Modifier.fillMaxSize().padding(innerPadding)) {
                    ShimmerListPlaceholder(modifier = Modifier.padding(Spacing.md), rows = 4)
                }
            }

            state.errorMessage != null && template == null -> {
                ErrorState(
                    message = state.errorMessage ?: "Unable to load checksheet template",
                    onRetry = viewModel::retry,
                    modifier = Modifier.fillMaxSize().padding(innerPadding),
                )
            }

            state.submitSuccess -> {
                // The form becomes read-only by no longer rendering any editable input at all -
                // DynamicFieldRenderer/components are never given a "disabled" mode (that would mean
                // touching the renderer, which this module must not do), so this screen simply stops
                // showing the interactive form once submitted, right before navigating away.
                Box(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(innerPadding),
                    contentAlignment = Alignment.Center
                ) {
                    com.checksheet.android.ui.components.loading.SavingSignalCelebration()
                }
            }

            template != null -> {
                LazyColumn(
                    state = listState,
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(innerPadding),
                    contentPadding = PaddingValues(Spacing.md),
                    verticalArrangement = Arrangement.spacedBy(Spacing.md)
                ) {
                    items(currentPageFields, key = { it.id }) { field ->
                        if (FieldType.fromBackendValue(field.fieldType) == FieldType.GROUP) {
                            GroupComponent(
                                field = field,
                                allFields = template.fields,
                                values = formState.values,
                                errors = formState.errors,
                                modifiedFields = formState.modifiedFields,
                                onValueChange = { fieldId, newValue -> viewModel.onFieldValueChanged(fieldId, newValue) }
                            )
                        } else {
                            // Module 31: every top-level checking point (not just groups) sits inside
                            // its own rounded "section card" - much easier to visually track one
                            // checking point at a time than the previous bare, unbounded list.
                            val hasError = field.id in formState.modifiedFields && formState.errors.containsKey(field.id)
                            val cinematic = com.checksheet.android.theme.RailwayTheme.cinematicColors
                            AppCard(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .border(
                                        width = 1.dp,
                                        color = if (hasError) MaterialTheme.colorScheme.error else cinematic.trackSteelDim,
                                        shape = MaterialTheme.shapes.medium,
                                    ),
                                containerColor = if (hasError) {
                                    MaterialTheme.colorScheme.errorContainer.copy(alpha = 0.15f)
                                } else {
                                    MaterialTheme.colorScheme.surface
                                },
                            ) {
                                Box(modifier = Modifier.padding(Spacing.md)) {
                                    DynamicFieldRenderer(
                                        field = field,
                                        value = formState.values[field.id].orEmpty(),
                                        onValueChange = { newValue -> viewModel.onFieldValueChanged(field.id, newValue) },
                                        errorMessage = if (field.id in formState.modifiedFields) {
                                            formState.errors[field.id]
                                        } else {
                                            null
                                        }
                                    )
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    if (showSubmitConfirmDialog) {
        AlertDialog(
            onDismissRequest = { showSubmitConfirmDialog = false },
            title = { Text("Submit Checksheet") },
            text = { Text("Once submitted, this checksheet can no longer be edited.") },
            confirmButton = {
                TextButton(onClick = {
                    showSubmitConfirmDialog = false
                    viewModel.submitChecksheet()
                }) {
                    Text("Submit")
                }
            },
            dismissButton = {
                TextButton(onClick = { showSubmitConfirmDialog = false }) {
                    Text("Cancel")
                }
            }
        )
    }
}
