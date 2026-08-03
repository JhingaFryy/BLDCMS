package com.checksheet.android.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.unit.dp
import com.checksheet.android.theme.RailwayTheme
import com.checksheet.android.theme.Spacing

/**
 * A Home Dashboard module card ("Railway Command Center" UI overhaul, building on Module 31's
 * [AppCard]): icon, title, description, soft elevation, rounded corners, press animation - the
 * last three come from [AppCard] itself. Icon badge restyled as a glowing "engineering panel"
 * roundel using the cinematic accent color instead of the plain primaryContainer circle.
 */
@Composable
fun ModuleCard(
    title: String,
    description: String,
    icon: ImageVector,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
) {
    val cinematic = RailwayTheme.cinematicColors
    AppCard(
        modifier = modifier.fillMaxWidth(),
        onClick = onClick,
        containerColor = MaterialTheme.colorScheme.surfaceContainer,
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .border(1.dp, cinematic.trackSteelDim, MaterialTheme.shapes.large)
                .padding(Spacing.md),
            horizontalAlignment = Alignment.Start,
        ) {
            Box(
                modifier = Modifier
                    .size(44.dp)
                    .background(
                        brush = Brush.radialGradient(listOf(cinematic.wireGlowDim, MaterialTheme.colorScheme.primaryContainer)),
                        shape = CircleShape,
                    )
                    .border(1.dp, cinematic.wireGlow.copy(alpha = 0.5f), CircleShape),
                contentAlignment = Alignment.Center,
            ) {
                Icon(
                    imageVector = icon,
                    contentDescription = null,
                    tint = MaterialTheme.colorScheme.onPrimaryContainer,
                    modifier = Modifier.size(24.dp),
                )
            }
            Spacer(modifier = Modifier.height(Spacing.sm))
            Text(text = title, style = MaterialTheme.typography.titleMedium)
            Spacer(modifier = Modifier.height(Spacing.xs))
            Text(
                text = description,
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
        }
    }
}
