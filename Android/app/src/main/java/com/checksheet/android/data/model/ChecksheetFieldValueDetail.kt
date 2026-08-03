package com.checksheet.android.data.model

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

/** Matches the backend's ChecksheetFieldValueResponse exactly (field metadata + the entered value). */
@Serializable
data class ChecksheetFieldValueDetail(
    @SerialName("field_id") val fieldId: Int,
    @SerialName("field_label") val fieldLabel: String,
    @SerialName("field_key") val fieldKey: String,
    @SerialName("field_type") val fieldType: String,
    @SerialName("display_order") val displayOrder: Int,
    val required: Boolean,
    val unit: String? = null,
    @SerialName("default_value") val defaultValue: String? = null,
    val options: String? = null,
    @SerialName("help_text") val helpText: String? = null,
    @SerialName("field_value") val fieldValue: String? = null,
    // Module 29.8: Standard/Authority reference values for the Supervisor Review screen -
    // field_label is already breadcrumb-flattened server-side (TemplateField.breadcrumb_label),
    // so a grouped leaf like "DE" always arrives already qualified, e.g. "Bearing Seat Dia. of
    // Rotor Shaft (for 6313) > DE".
    @SerialName("standard_value") val standardValue: String? = null,
    @SerialName("authority_reference") val authorityReference: String? = null
)
