package com.checksheet.android.ui.components.cinematic

import androidx.compose.animation.animateColorAsState
import androidx.compose.animation.core.tween
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.material3.MaterialTheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.unit.dp
import com.checksheet.android.theme.RailwayTheme

/**
 * "Railway Command Center" UI overhaul: a segmented "signal block" progress indicator - one
 * rounded segment per page, glowing for completed/current pages, dim for pages ahead. Replaces
 * the bare [androidx.compose.material3.LinearProgressIndicator] previously used for checksheet
 * page progress. Takes the SAME [currentPage]/[totalPages] values the screen already computes -
 * purely a different rendering of existing state, no new business data.
 */
@Composable
fun ProgressTimeline(currentPage: Int, totalPages: Int, modifier: Modifier = Modifier) {
    val colors = RailwayTheme.cinematicColors
    Row(
        modifier = modifier.fillMaxWidth().height(6.dp),
        horizontalArrangement = Arrangement.spacedBy(4.dp),
    ) {
        for (page in 1..totalPages) {
            val filled = page <= currentPage
            val segmentColor by animateColorAsState(
                targetValue = if (filled) colors.wireGlow else colors.trackSteelDim,
                animationSpec = tween(300),
                label = "timelineSegment",
            )
            Box(
                modifier = Modifier
                    .weight(1f)
                    .fillMaxSize()
                    .clip(MaterialTheme.shapes.extraSmall)
                    .background(segmentColor),
            )
        }
    }
}
