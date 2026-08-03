package com.checksheet.android.renderer.components

import androidx.compose.material3.Switch
import androidx.compose.runtime.Composable
import com.checksheet.android.data.model.TemplateField

@Composable
fun SwitchComponent(
    field: TemplateField,
    value: String,
    onValueChange: (String) -> Unit,
    errorMessage: String?
) {
    Switch(
        checked = value.equals("true", ignoreCase = true),
        onCheckedChange = { checked -> onValueChange(checked.toString()) }
    )
}
