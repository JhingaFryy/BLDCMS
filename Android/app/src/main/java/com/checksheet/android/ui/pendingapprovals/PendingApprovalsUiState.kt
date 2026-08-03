package com.checksheet.android.ui.pendingapprovals

data class PendingApprovalItem(
    val checksheetId: Int,
    val locoNumber: String,
    val locoType: String,
    val sectionName: String,
    val equipmentName: String,
    val technicianName: String,
    val submittedAtDisplay: String,
    val status: String
)

data class PendingApprovalsUiState(
    val loading: Boolean = true,
    val items: List<PendingApprovalItem> = emptyList(),
    val searchQuery: String = "",
    val statusFilter: String = "SUBMITTED",
    val errorMessage: String? = null
)
