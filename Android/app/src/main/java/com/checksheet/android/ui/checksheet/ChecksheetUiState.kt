package com.checksheet.android.ui.checksheet

import com.checksheet.android.data.model.ChecksheetTemplate

data class ChecksheetUiState(
    val loading: Boolean = true,
    val template: ChecksheetTemplate? = null,
    val formState: FormState = FormState(),
    val errorMessage: String? = null,
    val checksheetId: Int? = null,
    val isSubmitting: Boolean = false,
    val submitSuccess: Boolean = false,
    val submitError: String? = null,
    // Module 29.5: multi-page templates - 1-indexed, matching TemplateField.pageNumber.
    val currentPage: Int = 1
) {
    val totalPages: Int
        get() = template?.fields?.maxOfOrNull { it.pageNumber } ?: 1
}
