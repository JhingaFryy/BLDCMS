package com.checksheet.android.ui.checksheet

import com.checksheet.android.data.model.TemplateField
import com.checksheet.android.renderer.FieldType
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow

data class FormState(
    val values: Map<Int, String> = emptyMap(),
    val modifiedFields: Set<Int> = emptySet(),
    val errors: Map<Int, String> = emptyMap()
)

/**
 * Single source of truth for one checksheet form's values/validity.
 *
 * Individual field components never own business state - they only ever read [state] and
 * report changes back through [setValue]. This class is instantiated directly by
 * [ChecksheetViewModel] (one instance per form, not a Hilt-wide singleton).
 */
class FormStateManager {

    private val _state = MutableStateFlow(FormState())
    val state: StateFlow<FormState> = _state.asStateFlow()

    fun initialize(fields: List<TemplateField>) {
        val defaults = fields.associate { field -> field.id to (field.defaultValue ?: "") }
        _state.value = FormState(values = defaults)
    }

    fun setValue(fieldId: Int, value: String) {
        val current = _state.value
        _state.value = current.copy(
            values = current.values + (fieldId to value),
            modifiedFields = current.modifiedFields + fieldId,
            errors = current.errors - fieldId
        )
    }

    fun getValue(fieldId: Int): String = _state.value.values[fieldId].orEmpty()

    /** Marks the given fields as modified without changing their values, so their errors become visible. */
    fun touchAll(fieldIds: Collection<Int>) {
        val current = _state.value
        _state.value = current.copy(modifiedFields = current.modifiedFields + fieldIds)
    }

    /**
     * Re-validates every field (required / numeric / dropdown-option / date / time) and updates
     * [state]'s errors map. Returns true only when the whole form is currently valid.
     */
    fun validate(fields: List<TemplateField>): Boolean {
        val values = _state.value.values
        val errors = mutableMapOf<Int, String>()

        fields.forEach { field ->
            // GROUP fields are containers, not values - they have nothing of their own to
            // validate (their leaf children are validated individually, like any other field).
            if (FieldType.fromBackendValue(field.fieldType) == FieldType.GROUP) {
                return@forEach
            }

            val rawValue = values[field.id].orEmpty()

            if (field.required && rawValue.isBlank()) {
                errors[field.id] = "This field is required"
                return@forEach
            }

            if (rawValue.isNotBlank()) {
                when (FieldType.fromBackendValue(field.fieldType)) {
                    FieldType.NUMBER, FieldType.NUMERIC_RANGE -> {
                        if (rawValue.toDoubleOrNull() == null) {
                            errors[field.id] = "Enter a valid number"
                        }
                    }

                    FieldType.DROPDOWN -> {
                        val options = field.options
                            ?.split(",")
                            ?.map { it.trim() }
                            ?.filter { it.isNotBlank() }
                            ?: emptyList()
                        if (options.isNotEmpty() && rawValue !in options) {
                            errors[field.id] = "Select a valid option"
                        }
                    }

                    FieldType.DATE -> {
                        if (!DATE_PATTERN.matches(rawValue)) {
                            errors[field.id] = "Enter a valid date"
                        }
                    }

                    FieldType.TIME -> {
                        if (!TIME_PATTERN.matches(rawValue)) {
                            errors[field.id] = "Enter a valid time"
                        }
                    }

                    else -> Unit
                }
            }
        }

        _state.value = _state.value.copy(errors = errors)
        return errors.isEmpty()
    }

    fun clear() {
        _state.value = FormState()
    }

    private companion object {
        val DATE_PATTERN = Regex("""\d{4}-\d{2}-\d{2}""")
        val TIME_PATTERN = Regex("""\d{2}:\d{2}""")
    }
}
