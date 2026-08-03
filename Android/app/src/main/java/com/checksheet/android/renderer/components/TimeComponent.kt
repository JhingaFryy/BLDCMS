package com.checksheet.android.renderer.components

import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.AccessTime
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.TimePicker
import androidx.compose.material3.rememberTimePickerState
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import com.checksheet.android.data.model.TemplateField
import com.checksheet.android.ui.components.cinematic.railwayTextFieldColors

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun TimeComponent(
    field: TemplateField,
    value: String,
    onValueChange: (String) -> Unit,
    errorMessage: String?
) {
    var showPicker by remember { mutableStateOf(false) }

    OutlinedTextField(
        value = value,
        onValueChange = {},
        readOnly = true,
        isError = errorMessage != null,
        trailingIcon = {
            IconButton(onClick = { showPicker = true }) {
                Icon(imageVector = Icons.Filled.AccessTime, contentDescription = "Pick time")
            }
        },
        colors = railwayTextFieldColors(),
        modifier = Modifier.fillMaxWidth()
    )

    if (showPicker) {
        val timePickerState = rememberTimePickerState()
        AlertDialog(
            onDismissRequest = { showPicker = false },
            confirmButton = {
                TextButton(onClick = {
                    val hour = timePickerState.hour.toString().padStart(2, '0')
                    val minute = timePickerState.minute.toString().padStart(2, '0')
                    onValueChange("$hour:$minute")
                    showPicker = false
                }) {
                    Text("OK")
                }
            },
            dismissButton = {
                TextButton(onClick = { showPicker = false }) {
                    Text("Cancel")
                }
            },
            text = {
                TimePicker(state = timePickerState)
            }
        )
    }
}
