package com.checksheet.android.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import com.checksheet.android.theme.RailwayTheme
import com.checksheet.android.theme.Spacing

/**
 * Home Dashboard's Welcome Card ("Railway Command Center" UI overhaul, building on Module 31's
 * [AppCard]): profile image placeholder (initials avatar - no photo upload feature exists in this
 * app), technician name, employee ID, section, role badge. Restyled with a glow-accent border.
 */
@Composable
fun WelcomeCard(
    name: String,
    employeeId: String,
    section: String,
    role: String?,
    modifier: Modifier = Modifier,
) {
    val cinematic = RailwayTheme.cinematicColors
    AppCard(
        modifier = modifier
            .fillMaxWidth()
            .border(1.dp, cinematic.wireGlow.copy(alpha = 0.35f), MaterialTheme.shapes.large),
        containerColor = MaterialTheme.colorScheme.surfaceContainer,
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(Spacing.md),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            AvatarPlaceholder(name = name)
            Spacer(modifier = Modifier.width(Spacing.md))
            Column(modifier = Modifier.weight(1f)) {
                Text(text = "Welcome back,", style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
                Text(text = name, style = MaterialTheme.typography.headlineSmall)
                Spacer(modifier = Modifier.height(Spacing.xs))
                Text(
                    text = "ID $employeeId  •  $section",
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
                Spacer(modifier = Modifier.height(Spacing.sm))
                RoleBadge(role = role)
            }
        }
    }
}

/** Circular initials avatar used as the profile-image placeholder wherever a real photo isn't
 * available (Welcome Card, Profile screen) - shared so both stay visually identical. */
@Composable
fun AvatarPlaceholder(name: String, size: Dp = 56.dp) {
    Box(
        modifier = Modifier
            .size(size)
            .clip(CircleShape)
            .background(MaterialTheme.colorScheme.primaryContainer),
        contentAlignment = Alignment.Center,
    ) {
        Text(
            text = name.trim().firstOrNull()?.uppercaseChar()?.toString() ?: "?",
            style = MaterialTheme.typography.headlineSmall,
            color = MaterialTheme.colorScheme.onPrimaryContainer,
        )
    }
}
