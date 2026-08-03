package com.checksheet.android.ui.fillchecksheet

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.checksheet.android.data.model.Equipment
import com.checksheet.android.data.model.Locomotive
import com.checksheet.android.domain.repository.AuthRepository
import com.checksheet.android.domain.repository.ChecksheetTemplateRepository
import com.checksheet.android.domain.repository.EquipmentRepository
import com.checksheet.android.domain.repository.LocomotiveRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import retrofit2.HttpException
import java.io.IOException
import javax.inject.Inject

private const val SEARCH_DEBOUNCE_MS = 300L

@HiltViewModel
class FillChecksheetViewModel @Inject constructor(
    private val locomotiveRepository: LocomotiveRepository,
    private val equipmentRepository: EquipmentRepository,
    private val checksheetTemplateRepository: ChecksheetTemplateRepository,
    private val authRepository: AuthRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(FillChecksheetUiState())
    val uiState: StateFlow<FillChecksheetUiState> = _uiState.asStateFlow()

    private var searchJob: Job? = null
    private var templateResolutionJob: Job? = null
    private var equipmentJob: Job? = null

    init {
        loadCurrentUserSection()
    }

    fun onQueryChanged(rawQuery: String) {
        val digitsOnly = rawQuery.filter { it.isDigit() }.take(5)

        searchJob?.cancel()

        _uiState.value = _uiState.value.copy(
            query = digitsOnly,
            selectedLocomotive = null,
            errorMessage = null,
            resolvedTemplateId = null,
            templateError = null,
            selectedEquipment = null,
            equipmentList = emptyList(),
            isEquipmentlessSection = false,
            requiresMaintenanceTypeSelection = false,
            maintenanceTypeOptions = emptyList(),
            tractionMotorNumber = null,
            maintenanceType = null,
        )

        if (digitsOnly.isBlank()) {
            _uiState.value = _uiState.value.copy(isLoading = false, locomotives = emptyList())
            return
        }

        searchJob = viewModelScope.launch {
            delay(SEARCH_DEBOUNCE_MS)
            searchLocomotives(digitsOnly)
        }
    }

    fun retrySearch() {
        val query = _uiState.value.query
        if (query.isBlank()) return

        searchJob?.cancel()
        searchJob = viewModelScope.launch {
            searchLocomotives(query)
        }
    }

    fun onLocomotiveSelected(locomotive: Locomotive) {
        searchJob?.cancel()
        _uiState.value = _uiState.value.copy(
            selectedLocomotive = locomotive,
            query = locomotive.locoNumber,
            locomotives = emptyList(),
            errorMessage = null,
            resolvedTemplateId = null,
            templateError = null,
            // Module 29.12: the equipment list is specific to this locomotive's technology - any
            // equipment chosen for a previously selected locomotive is no longer necessarily valid.
            selectedEquipment = null,
            equipmentList = emptyList(),
            // Reset until the new fetch below actually completes - resolveTemplateIfReady() (called
            // synchronously just below) must not act on a stale value from a previous locomotive.
            isEquipmentlessSection = false,
            requiresMaintenanceTypeSelection = false,
            maintenanceTypeOptions = emptyList(),
            tractionMotorNumber = null,
            maintenanceType = null,
        )
        loadEquipment(locomotive.technology, locomotive.id)
        resolveTemplateIfReady()
    }

    fun onEquipmentSelected(equipment: Equipment) {
        _uiState.value = _uiState.value.copy(
            selectedEquipment = equipment,
            resolvedTemplateId = null,
            templateError = null,
            // Module 32: a Maintenance Type/TM Number chosen for a previously selected equipment
            // is no longer necessarily valid (or applicable) for the newly selected one.
            requiresMaintenanceTypeSelection = false,
            maintenanceTypeOptions = emptyList(),
            tractionMotorNumber = null,
            maintenanceType = null,
        )
        resolveTemplateIfReady()
    }

    fun onWorkTypeSelected(workType: String) {
        _uiState.value = _uiState.value.copy(workType = workType)
    }

    fun onTractionMotorNumberSelected(tractionMotorNumber: String) {
        _uiState.value = _uiState.value.copy(tractionMotorNumber = tractionMotorNumber)
    }

    /** Module 32: re-resolves the template once a Maintenance Type is chosen - the equipment's
     * candidate templates were already fetched by resolveTemplateIfReady(); this narrows them down
     * to the one matching this maintenance type instead of re-fetching. */
    fun onMaintenanceTypeSelected(maintenanceType: String) {
        _uiState.value = _uiState.value.copy(maintenanceType = maintenanceType, resolvedTemplateId = null, templateError = null)
        resolveTemplateIfReady()
    }

    fun retryTemplateResolution() {
        resolveTemplateIfReady()
    }

    /**
     * Once both a locomotive and an equipment are selected, resolves which ChecksheetTemplate
     * applies by matching the template's equipment_id and technology - the same technology vocabulary
     * already used to filter the equipment dropdown itself (Locomotive.technology). Reuses the
     * existing GET /templates/ endpoint (already used by the Dashboard); nothing invented.
     *
     * Module 32: some equipment (currently only Traction Motor) has more than one active template
     * for the same equipment+technology, disambiguated by maintenance_type (e.g. GC vs Overhaul) -
     * when that happens, resolution can't finish until the technician also picks a Maintenance
     * Type, so requiresMaintenanceTypeSelection/maintenanceTypeOptions are populated instead of an
     * immediate match. This is entirely data-driven off the templates actually returned by the
     * backend - nothing here is hardcoded to "Traction Motor" specifically, so any future
     * equipment that similarly grows a second template variant gets this behavior for free.
     *
     * Module 36: when [FillChecksheetUiState.isEquipmentlessSection] is true (e.g. M6-HR - see
     * loadEquipment below), there is no equipment to match against at all; candidates are instead
     * templates with a null equipment_id belonging to the technician's own section, matched by
     * technology alone. This mirrors the backend's own equipment-less template resolution
     * (section_id + technology, see checksheet_service._ensure_template_matches_selection) - still
     * entirely data-driven off whatever GET /templates/ actually returns, nothing hardcoded to
     * "M6-HR" specifically.
     */
    private fun resolveTemplateIfReady() {
        val locomotive = _uiState.value.selectedLocomotive ?: return
        val isEquipmentless = _uiState.value.isEquipmentlessSection
        val equipment = _uiState.value.selectedEquipment
        val sectionId = _uiState.value.sectionId
        if (!isEquipmentless && equipment == null) return
        if (isEquipmentless && sectionId == null) return

        templateResolutionJob?.cancel()
        templateResolutionJob = viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isResolvingTemplate = true, templateError = null)

            try {
                val templates = checksheetTemplateRepository.getTemplates()
                val candidates = templates.filter { template ->
                    template.technology == locomotive.technology &&
                        template.isActive &&
                        if (isEquipmentless) {
                            template.equipmentId == null && template.sectionId == sectionId
                        } else {
                            template.equipmentId == equipment?.id
                        }
                }

                if (candidates.size > 1) {
                    val maintenanceTypeOptions = candidates.mapNotNull { it.maintenanceType }.distinct()
                    val selectedMaintenanceType = _uiState.value.maintenanceType
                    val match = candidates.firstOrNull { it.maintenanceType == selectedMaintenanceType }

                    _uiState.value = _uiState.value.copy(
                        isResolvingTemplate = false,
                        resolvedTemplateId = match?.id,
                        requiresMaintenanceTypeSelection = true,
                        maintenanceTypeOptions = maintenanceTypeOptions,
                        templateError = if (selectedMaintenanceType != null && match == null) {
                            "No checksheet template found for the selected maintenance type."
                        } else null,
                    )
                    return@launch
                }

                val match = candidates.firstOrNull()
                _uiState.value = if (match != null) {
                    _uiState.value.copy(
                        isResolvingTemplate = false,
                        resolvedTemplateId = match.id,
                        requiresMaintenanceTypeSelection = false,
                        maintenanceTypeOptions = emptyList(),
                    )
                } else {
                    _uiState.value.copy(
                        isResolvingTemplate = false,
                        requiresMaintenanceTypeSelection = false,
                        maintenanceTypeOptions = emptyList(),
                        templateError = if (isEquipmentless) {
                            "No checksheet template found for this section and locomotive."
                        } else {
                            "No checksheet template found for this equipment and locomotive."
                        }
                    )
                }
            } catch (e: HttpException) {
                _uiState.value = _uiState.value.copy(
                    isResolvingTemplate = false,
                    templateError = "Unable to load checksheet template"
                )
            } catch (e: IOException) {
                _uiState.value = _uiState.value.copy(
                    isResolvingTemplate = false,
                    templateError = "Unable to load checksheet template"
                )
            } catch (e: Exception) {
                _uiState.value = _uiState.value.copy(
                    isResolvingTemplate = false,
                    templateError = "Unable to load checksheet template"
                )
            }
        }
    }

    private suspend fun searchLocomotives(query: String) {
        _uiState.value = _uiState.value.copy(isLoading = true, errorMessage = null)

        try {
            val results = locomotiveRepository.searchLocomotives(query)
            _uiState.value = _uiState.value.copy(isLoading = false, locomotives = results)
        } catch (e: HttpException) {
            _uiState.value = _uiState.value.copy(
                isLoading = false,
                locomotives = emptyList(),
                errorMessage = "Unable to load locomotives"
            )
        } catch (e: IOException) {
            _uiState.value = _uiState.value.copy(
                isLoading = false,
                locomotives = emptyList(),
                errorMessage = "Unable to load locomotives"
            )
        } catch (e: Exception) {
            _uiState.value = _uiState.value.copy(
                isLoading = false,
                locomotives = emptyList(),
                errorMessage = "Unable to load locomotives"
            )
        }
    }

    /** Module 29.12: called whenever the selected locomotive changes, so the Equipment dropdown
     * only ever offers equipment compatible with that locomotive's Technology. Filtering is done
     * server-side (see EquipmentRepository.getEquipmentForCurrentUser) - nothing is filtered here.
     *
     * Module 36: a successful fetch that comes back empty means the technician's section has no
     * equipment at all (e.g. M6-HR) - resolveTemplateIfReady() is triggered directly from here in
     * that case, since there is no onEquipmentSelected() to trigger it otherwise.
     *
     * Module 40: [locomotiveId] lets the backend additionally disambiguate by Locomotive Model
     * for sections that need it (e.g. M4-HR's WAG9HC vs WAP-7 equipment) - this app never decides
     * that itself, it only ever passes the id of whichever locomotive was actually selected. */
    private fun loadEquipment(technology: String, locomotiveId: Int) {
        equipmentJob?.cancel()
        equipmentJob = viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isEquipmentLoading = true)
            try {
                val equipment = equipmentRepository.getEquipmentForCurrentUser(technology, locomotiveId)
                val isEquipmentless = equipment.isEmpty()
                _uiState.value = _uiState.value.copy(
                    isEquipmentLoading = false,
                    equipmentList = equipment,
                    isEquipmentlessSection = isEquipmentless,
                )
                if (isEquipmentless) {
                    resolveTemplateIfReady()
                }
            } catch (e: HttpException) {
                _uiState.value = _uiState.value.copy(
                    isEquipmentLoading = false,
                    equipmentList = emptyList(),
                    errorMessage = "Unable to load equipment"
                )
            } catch (e: IOException) {
                _uiState.value = _uiState.value.copy(
                    isEquipmentLoading = false,
                    equipmentList = emptyList(),
                    errorMessage = "Unable to load equipment"
                )
            } catch (e: Exception) {
                _uiState.value = _uiState.value.copy(
                    isEquipmentLoading = false,
                    equipmentList = emptyList(),
                    errorMessage = "Unable to load equipment"
                )
            }
        }
    }

    private fun loadCurrentUserSection() {
        viewModelScope.launch {
            try {
                val profile = authRepository.getUserProfile()
                _uiState.value = _uiState.value.copy(sectionId = profile.sectionId)
            } catch (e: HttpException) {
                // Section id stays null; Continue remains disabled via the missing-context guard.
            } catch (e: IOException) {
                // Same as above - handled by the same guard rather than a separate error message.
            } catch (e: Exception) {
                // Same as above.
            }
        }
    }
}
