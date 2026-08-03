package com.checksheet.android.renderer.components

import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.input.KeyboardType
import com.checksheet.android.data.model.TemplateField
import com.checksheet.android.ui.components.cinematic.railwayTextFieldColors

@Composable
fun NumberFieldComponent(
    field: TemplateField,
    value: String,
    onValueChange: (String) -> Unit,
    errorMessage: String?
) {
    OutlinedTextField(
        value = value,
        onValueChange = { input ->
            val sanitized = input.filterIndexed { index, c ->
                c.isDigit() ||
                    (c == '.' && !input.take(index).contains('.')) ||
                    (c == '-' && index == 0)
            }
            onValueChange(sanitized)
        },
        singleLine = true,
        isError = errorMessage != null,
        trailingIcon = field.unit?.let { unit -> { Text(unit) } },
        keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Decimal),
        colors = railwayTextFieldColors(),
        modifier = Modifier.fillMaxWidth()
    )
}
