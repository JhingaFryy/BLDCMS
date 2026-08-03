package com.checksheet.android.ui.approvalreview

import com.checksheet.android.data.model.ChecksheetDetail

data class ApprovalReviewUiState(
    val loading: Boolean = true,
    val checksheet: ChecksheetDetail? = null,
    val errorMessage: String? = null,
    val isProcessing: Boolean = false,
    val actionSuccess: String? = null,
    val actionError: String? = null,
    val signatureStatus: SignatureStatus = SignatureStatus.UNKNOWN,
    val signatureInfo: SignatureInfo? = null
)
