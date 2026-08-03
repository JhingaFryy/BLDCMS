package com.checksheet.android.ui.components

import androidx.compose.foundation.layout.padding
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import com.checksheet.android.theme.RailwayTheme

/** A small colored pill for a user's role (Technician/Supervisor/Admin), used on the Home
 * Welcome Card and Profile screen. Falls back to a neutral tone for any unrecognized role string
 * rather than guessing - roles are backend-driven, not a fixed enum on the Android side. */
@Composable
fun RoleBadge(role: String?, modifier: Modifier = Modifier) {
    val (container, onContainer) = roleBadgeColors(role)
    Surface(
        modifier = modifier,
        shape = MaterialTheme.shapes.extraLarge,
        color = container,
    ) {
        Text(
            text = role ?: "Unknown",
            style = MaterialTheme.typography.labelMedium,
            color = onContainer,
            modifier = Modifier.padding(horizontal = 12.dp, vertical = 4.dp),
        )
    }
}

@Composable
private fun roleBadgeColors(role: String?): Pair<Color, Color> {
    val colorScheme = MaterialTheme.colorScheme
    val extended = RailwayTheme.extendedColors
    return when (role) {
        "Admin" -> extended.warningContainer to extended.onWarningContainer
        "Supervisor" -> colorScheme.tertiaryContainer to colorScheme.onTertiaryContainer
        "Technician" -> colorScheme.primaryContainer to colorScheme.onPrimaryContainer
        else -> colorScheme.surfaceVariant to colorScheme.onSurfaceVariant
    }
}
