package com.checksheet.android.renderer

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.checksheet.android.data.model.TemplateField
import com.checksheet.android.theme.Spacing

/**
 * Renders one template field: label + required indicator, the delegated input component
 * (resolved via [FieldRendererRegistry] - never a when() block here), then the validation message.
 */
@Composable
fun DynamicFieldRenderer(
    field: TemplateField,
    value: String,
    onValueChange: (String) -> Unit,
    errorMessage: String?
) {
    val fieldType = FieldType.fromBackendValue(field.fieldType)
    val component = FieldRendererRegistry.resolve(fieldType)

    Column(modifier = Modifier.fillMaxWidth()) {
        Row {
            Text(
                text = field.fieldLabel,
                style = MaterialTheme.typography.titleSmall
            )
            if (field.required) {
                Text(
                    text = " *",
                    style = MaterialTheme.typography.titleSmall,
                    color = MaterialTheme.colorScheme.error
                )
            }
        }

        field.helpText?.takeIf { it.isNotBlank() }?.let { helpText ->
            Text(
                text = helpText,
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }

        Spacer(modifier = Modifier.height(Spacing.xs))
        component(field, value, onValueChange, errorMessage)

        AnimatedVisibility(visible = errorMessage != null, enter = fadeIn(), exit = fadeOut()) {
            Text(
                text = errorMessage.orEmpty(),
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.error,
                modifier = Modifier.padding(top = 2.dp)
            )
        }
    }
}
