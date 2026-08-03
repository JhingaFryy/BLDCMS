package com.checksheet.android.data.model

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class TemplateField(
    val id: Int,
    @SerialName("template_id") val templateId: Int,
    @SerialName("field_key") val fieldKey: String,
    @SerialName("field_label") val fieldLabel: String,
    @SerialName("field_type") val fieldType: String,
    @SerialName("display_order") val displayOrder: Int,
    val required: Boolean,
    val unit: String? = null,
    @SerialName("default_value") val defaultValue: String? = null,
    val options: String? = null,
    @SerialName("help_text") val helpText: String? = null,
    @SerialName("is_active") val isActive: Boolean,
    // --- Module 29.5: Dynamic Checksheet Template Engine ---
    // All generic/reusable, mirroring app/schemas/template_field.py - never specific to any equipment.
    @SerialName("min_value") val minValue: Double? = null,
    @SerialName("max_value") val maxValue: Double? = null,
    @SerialName("decimal_precision") val decimalPrecision: Int? = null,
    @SerialName("standard_value") val standardValue: String? = null,
    @SerialName("authority_reference") val authorityReference: String? = null,
    @SerialName("parent_field_id") val parentFieldId: Int? = null,
    @SerialName("page_number") val pageNumber: Int = 1
)
