package com.checksheet.android.ui.fillchecksheet

import com.checksheet.android.data.model.Equipment
import com.checksheet.android.data.model.Locomotive

/** Module 29.8: the only two work types technicians choose from - a fixed, generic vocabulary,
 * not derived from any equipment/template data, so it applies identically to every checksheet. */
val WORK_TYPE_OPTIONS = listOf("IOH", "TOH")

/** Module 32: every locomotive has exactly six physical traction motors - a fixed vocabulary,
 * only ever shown once the resolved equipment turns out to need a Maintenance Type selection
 * (see FillChecksheetViewModel.resolveTemplateIfReady). */
val TRACTION_MOTOR_NUMBER_OPTIONS = listOf("TM-1", "TM-2", "TM-3", "TM-4", "TM-5", "TM-6")

data class FillChecksheetUiState(
    val query: String = "",
    val isLoading: Boolean = false,
    val locomotives: List<Locomotive> = emptyList(),
    val selectedLocomotive: Locomotive? = null,
    val equipmentList: List<Equipment> = emptyList(),
    val isEquipmentLoading: Boolean = false,
    val selectedEquipment: Equipment? = null,
    // Module 36: true once equipment finished loading for this locomotive's technology and came
    // back empty - the generic, data-driven signal that this section (e.g. M6-HR) has no equipment
    // at all, rather than a hardcoded section check. When true, the Equipment step is hidden and
    // template resolution proceeds on section_id + technology alone.
    val isEquipmentlessSection: Boolean = false,
    val errorMessage: String? = null,
    val sectionId: Int? = null,
    val isResolvingTemplate: Boolean = false,
    val resolvedTemplateId: Int? = null,
    val templateError: String? = null,
    // Module 29.8: required technician-selected Work Type, chosen here (before the checksheet
    // fill screen even loads) rather than left to the Supervisor at approval time.
    val workType: String? = null,
    // Module 32: only relevant once resolveTemplateIfReady() finds more than one active template
    // for the selected equipment+technology (currently only Traction Motor) - requiresMaintenanceTypeSelection
    // gates whether the TM Number/Maintenance Type dropdowns show at all, so every other
    // equipment's flow is completely unaffected.
    val requiresMaintenanceTypeSelection: Boolean = false,
    val maintenanceTypeOptions: List<String> = emptyList(),
    val tractionMotorNumber: String? = null,
    val maintenanceType: String? = null,
)
