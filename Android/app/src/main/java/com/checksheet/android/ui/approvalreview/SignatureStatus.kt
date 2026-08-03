package com.checksheet.android.ui.approvalreview

import com.checksheet.android.data.model.ChecksheetDetail

enum class SignatureStatus {
    PENDING_SIGNATURE,
    SIGNED,
    REJECTED,
    UNKNOWN
}

data class SignatureInfo(
    val signedBy: String?,
    val signatureDate: String?,
    val certificateName: String?,
    val certificateAuthority: String?
)

/**
 * The backend has no dedicated signature concept today, so this derives a best-effort status from
 * the checksheet's existing workflow `status` (APPROVED -> awaiting signature, REJECTED -> rejected,
 * anything else -> not applicable yet). If a future backend adds an explicit signature_status field,
 * that real value is preferred automatically - no Android change needed when that day comes.
 */
fun deriveSignatureStatus(checksheet: ChecksheetDetail): SignatureStatus {
    checksheet.signatureStatus?.let { raw ->
        return when (raw.trim().uppercase()) {
            "SIGNED" -> SignatureStatus.SIGNED
            "REJECTED" -> SignatureStatus.REJECTED
            "PENDING_SIGNATURE", "PENDING" -> SignatureStatus.PENDING_SIGNATURE
            else -> SignatureStatus.UNKNOWN
        }
    }

    return when (checksheet.status?.trim()?.uppercase()) {
        "APPROVED" -> SignatureStatus.PENDING_SIGNATURE
        "REJECTED" -> SignatureStatus.REJECTED
        else -> SignatureStatus.UNKNOWN
    }
}

/** Non-null only when the backend actually returned at least one signature metadata field. */
fun deriveSignatureInfo(checksheet: ChecksheetDetail): SignatureInfo? {
    if (checksheet.signedBy == null &&
        checksheet.signatureDate == null &&
        checksheet.certificateName == null &&
        checksheet.certificateAuthority == null
    ) {
        return null
    }

    return SignatureInfo(
        signedBy = checksheet.signedBy,
        signatureDate = checksheet.signatureDate,
        certificateName = checksheet.certificateName,
        certificateAuthority = checksheet.certificateAuthority
    )
}
