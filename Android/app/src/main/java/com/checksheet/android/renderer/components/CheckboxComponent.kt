package com.checksheet.android.renderer.components

import androidx.compose.material3.Checkbox
import androidx.compose.runtime.Composable
import com.checksheet.android.data.model.TemplateField

@Composable
fun CheckboxComponent(
    field: TemplateField,
    value: String,
    onValueChange: (String) -> Unit,
    errorMessage: String?
) {
    Checkbox(
        checked = value.equals("true", ignoreCase = true),
        onCheckedChange = { checked -> onValueChange(checked.toString()) }
    )
}
