package com.checksheet.android.renderer.components

import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.CalendarMonth
import androidx.compose.material3.DatePicker
import androidx.compose.material3.DatePickerDialog
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.rememberDatePickerState
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import com.checksheet.android.data.model.TemplateField
import com.checksheet.android.ui.components.cinematic.railwayTextFieldColors
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun DateComponent(
    field: TemplateField,
    value: String,
    onValueChange: (String) -> Unit,
    errorMessage: String?
) {
    var showPicker by remember { mutableStateOf(false) }
    val formatter = remember { SimpleDateFormat("yyyy-MM-dd", Locale.US) }

    OutlinedTextField(
        value = value,
        onValueChange = {},
        readOnly = true,
        isError = errorMessage != null,
        trailingIcon = {
            IconButton(onClick = { showPicker = true }) {
                Icon(imageVector = Icons.Filled.CalendarMonth, contentDescription = "Pick date")
            }
        },
        colors = railwayTextFieldColors(),
        modifier = Modifier.fillMaxWidth()
    )

    if (showPicker) {
        val datePickerState = rememberDatePickerState()
        DatePickerDialog(
            onDismissRequest = { showPicker = false },
            confirmButton = {
                TextButton(onClick = {
                    val millis = datePickerState.selectedDateMillis
                    if (millis != null) {
                        onValueChange(formatter.format(Date(millis)))
                    }
                    showPicker = false
                }) {
                    Text("OK")
                }
            },
            dismissButton = {
                TextButton(onClick = { showPicker = false }) {
                    Text("Cancel")
                }
            }
        ) {
            DatePicker(state = datePickerState)
        }
    }
}
