package com.checksheet.android.renderer.components

import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.material3.OutlinedTextField
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import com.checksheet.android.data.model.TemplateField
import com.checksheet.android.ui.components.cinematic.railwayTextFieldColors

@Composable
fun TextFieldComponent(
    field: TemplateField,
    value: String,
    onValueChange: (String) -> Unit,
    errorMessage: String?
) {
    OutlinedTextField(
        value = value,
        onValueChange = onValueChange,
        singleLine = true,
        isError = errorMessage != null,
        colors = railwayTextFieldColors(),
        modifier = Modifier.fillMaxWidth()
    )
}
