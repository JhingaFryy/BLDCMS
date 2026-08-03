package com.checksheet.android.ui.components.cinematic

import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextFieldDefaults
import androidx.compose.material3.TextFieldColors
import androidx.compose.runtime.Composable
import com.checksheet.android.theme.RailwayTheme

/**
 * "Railway Command Center" UI overhaul: shared [OutlinedTextField] color scheme for every
 * redesigned screen (Login, OTP, Checksheet fields) - a single helper so restyling every field
 * across the app is a one-line swap per call site (`colors = railwayTextFieldColors()`) rather
 * than a rewrite of each field's layout/logic.
 */
@Composable
fun railwayTextFieldColors(): TextFieldColors {
    val colors = RailwayTheme.cinematicColors
    return OutlinedTextFieldDefaults.colors(
        focusedBorderColor = colors.wireGlow,
        unfocusedBorderColor = colors.trackSteel,
        focusedLabelColor = colors.wireGlow,
        cursorColor = colors.wireGlow,
        focusedLeadingIconColor = colors.wireGlow,
        unfocusedLeadingIconColor = MaterialTheme.colorScheme.onSurfaceVariant,
        focusedTrailingIconColor = colors.wireGlow,
    )
}
