package com.checksheet.android.renderer.components

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.checksheet.android.data.model.TemplateField

@Composable
fun ReadOnlyComponent(
    field: TemplateField,
    value: String,
    onValueChange: (String) -> Unit,
    errorMessage: String?
) {
    Text(
        text = value.ifBlank { field.defaultValue ?: "-" },
        style = MaterialTheme.typography.bodyLarge,
        modifier = Modifier
            .fillMaxWidth()
            .background(
                color = MaterialTheme.colorScheme.surfaceVariant,
                shape = MaterialTheme.shapes.small
            )
            .padding(12.dp)
    )
}
