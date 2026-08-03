package com.checksheet.android.ui.checksheetdetail

import com.checksheet.android.data.model.ChecksheetDetail

data class ChecksheetDetailUiState(
    val loading: Boolean = true,
    val checksheet: ChecksheetDetail? = null,
    val errorMessage: String? = null,
    val isPdfBusy: Boolean = false,
    val pdfDownloaded: Boolean = false,
    val pdfError: String? = null
)
