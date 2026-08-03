package com.checksheet.android.renderer.components

import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.focus.onFocusChanged
import androidx.compose.ui.text.input.KeyboardType
import com.checksheet.android.data.model.TemplateField
import com.checksheet.android.ui.components.cinematic.railwayTextFieldColors
import kotlin.math.pow
import kotlin.math.round

/**
 * Reusable Numeric Range field (Module 29.5, field type 1) - min/max/unit/precision all come from
 * the template ([TemplateField.minValue]/[maxValue]/[unit]/[decimalPrecision]), never hardcoded.
 *
 * Typed input is held locally and NOT committed via [onValueChange] until focus is lost: if the
 * number is within [min, max] it commits silently; if it's outside range, a confirmation dialog
 * is shown and the value is only committed if the technician explicitly confirms it - otherwise
 * the edit is discarded and the field reverts to its last committed value.
 */
@Composable
fun NumericRangeComponent(
    field: TemplateField,
    value: String,
    onValueChange: (String) -> Unit,
    errorMessage: String?
) {
    var localText by remember(value) { mutableStateOf(value) }
    var pendingOutOfRangeValue by remember { mutableStateOf<String?>(null) }

    fun commit(rawText: String) {
        val parsed = rawText.toDoubleOrNull()
        val min = field.minValue
        val max = field.maxValue

        if (parsed == null) {
            // Not a parseable number (e.g. blank, or mid-edit) - leave commit to normal form
            // validation rather than silently discarding what the technician typed.
            onValueChange(rawText)
            return
        }

        val rounded = field.decimalPrecision?.let { precision ->
            val factor = 10.0.pow(precision)
            round(parsed * factor) / factor
        } ?: parsed
        val formatted = if (field.decimalPrecision != null) {
            "%.${field.decimalPrecision}f".format(rounded)
        } else {
            rawText
        }

        val outOfRange = (min != null && rounded < min) || (max != null && rounded > max)
        if (outOfRange) {
            pendingOutOfRangeValue = formatted
        } else {
            onValueChange(formatted)
        }
    }

    OutlinedTextField(
        value = localText,
        onValueChange = { input ->
            localText = input.filterIndexed { index, c ->
                c.isDigit() ||
                    (c == '.' && !input.take(index).contains('.')) ||
                    (c == '-' && index == 0)
            }
        },
        singleLine = true,
        isError = errorMessage != null,
        trailingIcon = field.unit?.let { unit -> { Text(unit) } },
        keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Decimal),
        colors = railwayTextFieldColors(),
        modifier = Modifier
            .fillMaxWidth()
            .onFocusChanged { focusState ->
                if (!focusState.isFocused) {
                    commit(localText)
                }
            }
    )

    val pending = pendingOutOfRangeValue
    if (pending != null) {
        AlertDialog(
            onDismissRequest = {
                localText = value
                pendingOutOfRangeValue = null
            },
            title = { Text("Value Out of Range") },
            text = { Text("Entered value is outside the prescribed standard.") },
            confirmButton = {
                TextButton(onClick = {
                    onValueChange(pending)
                    pendingOutOfRangeValue = null
                }) {
                    Text("I Confirm This Reading")
                }
            },
            dismissButton = {
                TextButton(onClick = {
                    localText = value
                    pendingOutOfRangeValue = null
                }) {
                    Text("Cancel")
                }
            }
        )
    }
}
