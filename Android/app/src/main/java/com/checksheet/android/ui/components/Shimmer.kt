package com.checksheet.android.ui.components

import androidx.compose.animation.core.LinearEasing
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material3.MaterialTheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Shape
import androidx.compose.ui.unit.dp
import com.checksheet.android.theme.Spacing

/**
 * A shimmering brush for skeleton loading placeholders (Module 31 - "Loading shimmer"). Colors
 * are drawn from the theme's surface-variant role (never hardcoded grey), so it looks correct in
 * both light and dark mode automatically.
 */
@Composable
fun rememberShimmerBrush(): Brush {
    val base = MaterialTheme.colorScheme.surfaceVariant
    val highlight = MaterialTheme.colorScheme.surface
    val transition = rememberInfiniteTransition(label = "shimmer")
    val translateAnim by transition.animateFloat(
        initialValue = 0f,
        targetValue = 1000f,
        animationSpec = infiniteRepeatable(
            animation = tween(durationMillis = 1100, easing = LinearEasing),
            repeatMode = RepeatMode.Restart,
        ),
        label = "shimmerTranslate",
    )
    return Brush.linearGradient(
        colors = listOf(base, highlight, base),
        start = Offset(translateAnim - 500f, 0f),
        end = Offset(translateAnim, 0f),
    )
}

/** A single shimmering rectangle - the basic building block every skeleton below composes. */
@Composable
fun ShimmerBlock(modifier: Modifier = Modifier, shape: Shape = MaterialTheme.shapes.small) {
    val brush = rememberShimmerBrush()
    Box(modifier = modifier.clip(shape).background(brush))
}

/** A skeleton standing in for a [ModuleCard]/list card while real data loads. */
@Composable
fun ShimmerCard(modifier: Modifier = Modifier) {
    AppCard(modifier = modifier.fillMaxWidth()) {
        Column(modifier = Modifier.fillMaxWidth().padding(Spacing.md)) {
            ShimmerBlock(modifier = Modifier.size(44.dp), shape = CircleShape)
            Spacer(modifier = Modifier.height(Spacing.sm))
            ShimmerBlock(modifier = Modifier.fillMaxWidth(0.6f).height(16.dp))
            Spacer(modifier = Modifier.height(Spacing.xs))
            ShimmerBlock(modifier = Modifier.fillMaxWidth(0.9f).height(12.dp))
        }
    }
}

/** A skeleton standing in for a single-line list row (history/pending-approval rows) while
 * loading, so the list's eventual layout doesn't visually "pop in" against a bare spinner. */
@Composable
fun ShimmerListRow(modifier: Modifier = Modifier) {
    AppCard(modifier = modifier.fillMaxWidth()) {
        Row(
            modifier = Modifier.fillMaxWidth().padding(Spacing.md),
            horizontalArrangement = Arrangement.spacedBy(Spacing.md),
        ) {
            ShimmerBlock(modifier = Modifier.size(40.dp), shape = CircleShape)
            Column(modifier = Modifier.weight(1f), verticalArrangement = Arrangement.spacedBy(Spacing.xs)) {
                ShimmerBlock(modifier = Modifier.fillMaxWidth(0.5f).height(14.dp))
                ShimmerBlock(modifier = Modifier.fillMaxWidth(0.8f).height(12.dp))
            }
        }
    }
}

/** A vertical stack of [ShimmerListRow]s, for screens showing a `LazyColumn` of similar cards. */
@Composable
fun ShimmerListPlaceholder(modifier: Modifier = Modifier, rows: Int = 5) {
    Column(modifier = modifier.fillMaxWidth(), verticalArrangement = Arrangement.spacedBy(Spacing.sm)) {
        repeat(rows) { ShimmerListRow() }
    }
}
