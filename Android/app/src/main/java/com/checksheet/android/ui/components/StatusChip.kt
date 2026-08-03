package com.checksheet.android.ui.components

import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Cancel
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.Edit
import androidx.compose.material.icons.filled.HelpOutline
import androidx.compose.material.icons.filled.HourglassEmpty
import androidx.compose.material.icons.filled.Visibility
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.width
import androidx.compose.ui.Alignment
import androidx.compose.ui.unit.dp
import com.checksheet.android.theme.RailwayTheme
import com.checksheet.android.ui.history.ChecksheetLifecycleStatus

/**
 * Read-only status chip, promoted out of ui/history (Module 31) so ChecksheetDetail/History/
 * ApprovalReview can all share one presentation without duplicating the status->color mapping.
 * Filled-tonal style (container + onContainer) rather than a bordered/outline chip - reads more
 * clearly at a glance in an industrial field-use context. Colors come exclusively from
 * MaterialTheme.colorScheme / RailwayTheme.extendedColors roles, never hardcoded RGB, so each
 * status stays meaningful: Signed uses Railway Green (success), Under Review uses Amber
 * (warning), Rejected uses Material Red (error), Needs Correction uses Safety Orange (tertiary).
 */
@Composable
fun StatusChip(status: ChecksheetLifecycleStatus, modifier: Modifier = Modifier) {
    val (label, icon, container, onContainer) = statusChipContent(status)
    Surface(
        modifier = modifier,
        shape = MaterialTheme.shapes.extraLarge,
        color = container,
    ) {
        Row(
            modifier = Modifier.padding(horizontal = 12.dp, vertical = 6.dp),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Icon(imageVector = icon, contentDescription = null, tint = onContainer, modifier = Modifier.size(16.dp))
            Spacer(modifier = Modifier.width(6.dp))
            Text(text = label, color = onContainer, style = MaterialTheme.typography.labelLarge)
        }
    }
}

private data class StatusChipContent(
    val label: String,
    val icon: ImageVector,
    val container: Color,
    val onContainer: Color,
)

@Composable
private fun statusChipContent(status: ChecksheetLifecycleStatus): StatusChipContent {
    val extended = RailwayTheme.extendedColors
    val colorScheme = MaterialTheme.colorScheme
    return when (status) {
        ChecksheetLifecycleStatus.SUBMITTED ->
            StatusChipContent("Submitted", Icons.Filled.HourglassEmpty, colorScheme.primaryContainer, colorScheme.onPrimaryContainer)

        ChecksheetLifecycleStatus.UNDER_REVIEW ->
            StatusChipContent("Under Review", Icons.Filled.Visibility, extended.warningContainer, extended.onWarningContainer)

        ChecksheetLifecycleStatus.SIGNED ->
            StatusChipContent("Signed", Icons.Filled.CheckCircle, extended.successContainer, extended.onSuccessContainer)

        ChecksheetLifecycleStatus.REJECTED ->
            StatusChipContent("Rejected", Icons.Filled.Cancel, colorScheme.errorContainer, colorScheme.onErrorContainer)

        ChecksheetLifecycleStatus.NEEDS_CORRECTION ->
            StatusChipContent("Needs Correction", Icons.Filled.Edit, colorScheme.tertiaryContainer, colorScheme.onTertiaryContainer)

        ChecksheetLifecycleStatus.UNKNOWN ->
            StatusChipContent("Unknown", Icons.Filled.HelpOutline, colorScheme.surfaceVariant, colorScheme.onSurfaceVariant)
    }
}
