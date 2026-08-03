package com.checksheet.android.ui.checksheet

import androidx.lifecycle.SavedStateHandle
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.checksheet.android.data.model.ChecksheetFieldValue
import com.checksheet.android.domain.repository.ChecksheetRepository
import com.checksheet.android.domain.repository.ChecksheetTemplateRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.Job
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import retrofit2.HttpException
import java.io.IOException
import javax.inject.Inject

@HiltViewModel
class ChecksheetViewModel @Inject constructor(
    private val checksheetTemplateRepository: ChecksheetTemplateRepository,
    private val checksheetRepository: ChecksheetRepository,
    savedStateHandle: SavedStateHandle
) : ViewModel() {

    private val templateId: Int? = savedStateHandle.get<String>("templateId")?.toIntOrNull()

    // Not yet threaded through navigation by any module (ChecksheetScreen itself isn't wired into
    // MainActivity's nav graph yet - see Module 12's summary). Sourced the same way as templateId,
    // ready for a future module's navigation wiring; submitChecksheet() fails gracefully if absent.
    private val locomotiveId: Int? = savedStateHandle.get<String>("locomotiveId")?.toIntOrNull()
    private val sectionId: Int? = savedStateHandle.get<String>("sectionId")?.toIntOrNull()
    private val equipmentId: Int? = savedStateHandle.get<String>("equipmentId")?.toIntOrNull()

    // Module 29.8: chosen by the technician on FillChecksheetScreen before this screen is ever
    // reached (the nav route always supplies it - see MainActivity's "checksheet/.../{workType}"
    // route), so there is no default/fallback here anymore; a missing value fails submission
    // explicitly via the same "Unable to submit checksheet" guard as a missing locomotive/section/equipment.
    private val workType: String? = savedStateHandle.get<String>("workType")?.takeIf { it.isNotBlank() }

    // Module 32: optional checksheet-level metadata (null for every equipment other than
    // Traction Motor) - sourced the same way workType already is, from the nav route's
    // query-style args (see MainActivity's "checksheet/...?tmNumber=...&maintenanceType=..." route).
    private val tractionMotorNumber: String? = savedStateHandle.get<String>("tmNumber")?.takeIf { it.isNotBlank() }
    private val maintenanceType: String? = savedStateHandle.get<String>("maintenanceType")?.takeIf { it.isNotBlank() }

    private val formStateManager = FormStateManager()

    private val _uiState = MutableStateFlow(ChecksheetUiState())
    val uiState: StateFlow<ChecksheetUiState> = _uiState.asStateFlow()

    private var loadJob: Job? = null
    private var submitJob: Job? = null

    init {
        loadTemplate()
    }

    fun retry() {
        loadTemplate()
    }

    fun nextPage() {
        val state = _uiState.value
        _uiState.value = state.copy(currentPage = (state.currentPage + 1).coerceAtMost(state.totalPages))
    }

    fun previousPage() {
        val state = _uiState.value
        _uiState.value = state.copy(currentPage = (state.currentPage - 1).coerceAtLeast(1))
    }

    fun goToPage(page: Int) {
        val state = _uiState.value
        _uiState.value = state.copy(currentPage = page.coerceIn(1, state.totalPages))
    }

    fun onFieldValueChanged(fieldId: Int, value: String) {
        formStateManager.setValue(fieldId, value)
        revalidate()
    }

    /** Re-runs validation against the current template and returns whether the form is fully valid. */
    fun validate(): Boolean {
        val fields = _uiState.value.template?.fields ?: return false
        val isValid = formStateManager.validate(fields)
        syncFormState()
        return isValid
    }

    /**
     * Runs full validation and, if anything is invalid, marks every invalid field as "modified" so
     * DynamicFieldRenderer shows its error text even for fields the technician never touched - this is
     * the explicit highlight-on-submit-attempt behavior; live-typing validation deliberately does not
     * do this (see revalidate()), so a pristine required field doesn't show an error before it's due to.
     * Returns true only when the form is fully valid and safe to proceed to the confirmation dialog.
     */
    fun validateForSubmit(): Boolean {
        val fields = _uiState.value.template?.fields ?: return false
        val isValid = formStateManager.validate(fields)
        if (!isValid) {
            formStateManager.touchAll(formStateManager.state.value.errors.keys)
        }
        syncFormState()
        return isValid
    }

    /**
     * Submits the checksheet in a single user-facing action - there is no separate "save as draft"
     * step exposed anywhere in the app. If the header row hasn't been created on the backend yet,
     * it's created here first (the backend's status machine requires every row to start as DRAFT
     * before it can transition to SUBMITTED), then immediately moved to SUBMITTED, back-to-back,
     * so the app never leaves a checksheet sitting in Draft status for the user to return to.
     * Callers must have already confirmed via validateForSubmit() returning true (the confirmation
     * dialog only opens in that case), but this re-checks defensively rather than trusting stale state.
     */
    fun submitChecksheet() {
        if (_uiState.value.isSubmitting || _uiState.value.submitSuccess) return

        if (formStateManager.state.value.errors.isNotEmpty()) {
            _uiState.value = _uiState.value.copy(submitError = "Please complete all mandatory fields.")
            return
        }

        val effectiveWorkType = workType

        submitJob?.cancel()
        submitJob = viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isSubmitting = true, submitError = null)

            try {
                var id = _uiState.value.checksheetId
                if (id == null) {
                    val loco = locomotiveId
                    val section = sectionId
                    // Module 36: null for an equipment-less section (e.g. M6-HR) - not part of the
                    // required-fields guard below, unlike locomotive/section/template/workType.
                    val equipment = equipmentId
                    val tmplId = templateId

                    if (tmplId == null || loco == null || section == null || effectiveWorkType == null) {
                        _uiState.value = _uiState.value.copy(
                            isSubmitting = false,
                            submitError = "Unable to submit checksheet."
                        )
                        return@launch
                    }

                    val values = formStateManager.state.value.values.map { (fieldId, value) ->
                        ChecksheetFieldValue(fieldId = fieldId, value = value)
                    }
                    val created = checksheetRepository.saveDraft(
                        checksheetId = null,
                        locomotiveId = loco,
                        sectionId = section,
                        equipmentId = equipment,
                        templateId = tmplId,
                        workType = effectiveWorkType,
                        tractionMotorNumber = tractionMotorNumber,
                        maintenanceType = maintenanceType,
                        values = values
                    )
                    id = created.id
                    _uiState.value = _uiState.value.copy(checksheetId = id)
                }

                if (effectiveWorkType == null) {
                    _uiState.value = _uiState.value.copy(isSubmitting = false, submitError = "Unable to submit checksheet.")
                    return@launch
                }

                checksheetRepository.submitChecksheet(id, effectiveWorkType)
                formStateManager.clear()
                _uiState.value = _uiState.value.copy(
                    isSubmitting = false,
                    submitSuccess = true,
                    formState = formStateManager.state.value
                )
            } catch (e: HttpException) {
                _uiState.value = _uiState.value.copy(isSubmitting = false, submitError = "Unable to submit checksheet.")
            } catch (e: IOException) {
                _uiState.value = _uiState.value.copy(isSubmitting = false, submitError = "Unable to submit checksheet.")
            } catch (e: Exception) {
                _uiState.value = _uiState.value.copy(isSubmitting = false, submitError = "Unable to submit checksheet.")
            }
        }
    }

    fun onSubmitErrorMessageShown() {
        _uiState.value = _uiState.value.copy(submitError = null)
    }

    private fun revalidate() {
        _uiState.value.template?.fields?.let { fields -> formStateManager.validate(fields) }
        syncFormState()
    }

    private fun syncFormState() {
        _uiState.value = _uiState.value.copy(formState = formStateManager.state.value)
    }

    private fun loadTemplate() {
        val id = templateId
        if (id == null) {
            _uiState.value = _uiState.value.copy(
                loading = false,
                errorMessage = "No checksheet template selected"
            )
            return
        }

        loadJob?.cancel()
        loadJob = viewModelScope.launch {
            _uiState.value = _uiState.value.copy(loading = true, errorMessage = null)

            try {
                val template = checksheetTemplateRepository.getTemplate(id, sectionId)
                formStateManager.initialize(template.fields)
                formStateManager.validate(template.fields)
                _uiState.value = _uiState.value.copy(
                    loading = false,
                    template = template,
                    formState = formStateManager.state.value,
                    errorMessage = null,
                    currentPage = 1
                )
            } catch (e: HttpException) {
                _uiState.value = _uiState.value.copy(
                    loading = false,
                    errorMessage = "Unable to load checksheet template"
                )
            } catch (e: IOException) {
                _uiState.value = _uiState.value.copy(
                    loading = false,
                    errorMessage = "Unable to load checksheet template"
                )
            } catch (e: Exception) {
                _uiState.value = _uiState.value.copy(
                    loading = false,
                    errorMessage = "Unable to load checksheet template"
                )
            }
        }
    }
}
