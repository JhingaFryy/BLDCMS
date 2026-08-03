package com.checksheet.android.data.model

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class ChecksheetTemplate(
    val id: Int,
    @SerialName("template_code") val templateCode: String,
    val version: Int,
    // Nullable as of Module 29.5: a section-wide "common page" template (fetched only indirectly,
    // composed into an equipment template's own response) has no equipment_id of its own. An
    // equipment template fetched normally always has this set.
    @SerialName("equipment_id") val equipmentId: Int? = null,
    @SerialName("section_id") val sectionId: Int? = null,
    val technology: String,
    // Module 32: set only when this template shares (equipment_id, technology) with another
    // active template - e.g. Traction Motor's GC vs Overhaul checksheets - null for every other
    // equipment, where equipment_id+technology alone still resolves to exactly one template.
    @SerialName("maintenance_type") val maintenanceType: String? = null,
    @SerialName("template_name") val templateName: String,
    val description: String? = null,
    @SerialName("is_active") val isActive: Boolean,
    val fields: List<TemplateField> = emptyList()
)
