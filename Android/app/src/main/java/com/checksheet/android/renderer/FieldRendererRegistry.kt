package com.checksheet.android.renderer

import androidx.compose.runtime.Composable
import com.checksheet.android.data.model.TemplateField
import com.checksheet.android.renderer.components.CheckboxComponent
import com.checksheet.android.renderer.components.DateComponent
import com.checksheet.android.renderer.components.DropdownComponent
import com.checksheet.android.renderer.components.MultilineComponent
import com.checksheet.android.renderer.components.NumberFieldComponent
import com.checksheet.android.renderer.components.NumericRangeComponent
import com.checksheet.android.renderer.components.ReadOnlyComponent
import com.checksheet.android.renderer.components.SwitchComponent
import com.checksheet.android.renderer.components.TextFieldComponent
import com.checksheet.android.renderer.components.TimeComponent
import com.checksheet.android.renderer.components.UnsupportedFieldComponent

typealias FieldComponent = @Composable (
    field: TemplateField,
    value: String,
    onValueChange: (String) -> Unit,
    errorMessage: String?
) -> Unit

/**
 * Maps a [FieldType] to the composable that renders it.
 *
 * Adding a new field type (e.g. IMAGE, SIGNATURE, GPS, BARCODE, QR_CODE, FILE_UPLOAD) never requires
 * touching DynamicFieldRenderer or ChecksheetScreen - only a new Component file and one new map entry here.
 */
object FieldRendererRegistry {

    private val registry: Map<FieldType, FieldComponent> = mapOf(
        FieldType.TEXT to { field, value, onValueChange, error ->
            TextFieldComponent(field, value, onValueChange, error)
        },
        FieldType.NUMBER to { field, value, onValueChange, error ->
            NumberFieldComponent(field, value, onValueChange, error)
        },
        FieldType.NUMERIC_RANGE to { field, value, onValueChange, error ->
            NumericRangeComponent(field, value, onValueChange, error)
        },
        // GROUP has no scalar value of its own - it's a container rendered recursively via
        // GroupComponent, invoked directly by ChecksheetScreen (see GroupComponent's doc comment).
        // This entry only guards against a stray GROUP field ever reaching the generic scalar path.
        FieldType.GROUP to { _, _, _, _ -> },
        FieldType.BOOLEAN to { field, value, onValueChange, error ->
            SwitchComponent(field, value, onValueChange, error)
        },
        FieldType.CHECKBOX to { field, value, onValueChange, error ->
            CheckboxComponent(field, value, onValueChange, error)
        },
        FieldType.DROPDOWN to { field, value, onValueChange, error ->
            DropdownComponent(field, value, onValueChange, error)
        },
        FieldType.MULTILINE_TEXT to { field, value, onValueChange, error ->
            MultilineComponent(field, value, onValueChange, error)
        },
        FieldType.DATE to { field, value, onValueChange, error ->
            DateComponent(field, value, onValueChange, error)
        },
        FieldType.TIME to { field, value, onValueChange, error ->
            TimeComponent(field, value, onValueChange, error)
        },
        FieldType.READ_ONLY to { field, value, onValueChange, error ->
            ReadOnlyComponent(field, value, onValueChange, error)
        }
    )

    private val unknown: FieldComponent = { field, value, onValueChange, error ->
        UnsupportedFieldComponent(field, value, onValueChange, error)
    }

    fun resolve(fieldType: FieldType): FieldComponent = registry[fieldType] ?: unknown
}
