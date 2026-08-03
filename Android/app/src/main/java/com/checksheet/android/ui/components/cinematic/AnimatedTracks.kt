package com.checksheet.android.ui.components.cinematic

import androidx.compose.animation.core.LinearEasing
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import com.checksheet.android.theme.RailwayTheme

/**
 * "Railway Command Center" UI overhaul: a pair of railway rails in perspective (converging toward
 * a vanishing point) with regularly-spaced sleepers and a headlight streak that sweeps along the
 * rails on a loop. Used behind the locomotive on the Splash sequence and as a subtle motif on the
 * loading animations. Purely decorative Canvas art - no state, no business logic.
 */
@Composable
fun AnimatedTracks(modifier: Modifier = Modifier, trackHeight: Dp = 160.dp, sleeperCount: Int = 10) {
    val colors = RailwayTheme.cinematicColors
    val transition = rememberInfiniteTransition(label = "tracksSweep")
    val sweep by transition.animateFloat(
        initialValue = -0.2f,
        targetValue = 1.2f,
        animationSpec = infiniteRepeatable(tween(2600, easing = LinearEasing), RepeatMode.Restart),
        label = "headlightSweep",
    )

    Canvas(modifier = modifier.fillMaxWidth().height(trackHeight)) {
        val w = size.width
        val h = size.height
        val vanishX = w / 2f
        val vanishY = 0f

        // Rails converge from the bottom corners toward a vanishing point above the visible area,
        // giving a receding-into-the-distance perspective.
        val leftBottom = Offset(w * 0.12f, h)
        val rightBottom = Offset(w * 0.88f, h)
        val leftTop = Offset(vanishX - w * 0.04f, vanishY)
        val rightTop = Offset(vanishX + w * 0.04f, vanishY)

        drawLine(colors.trackSteel, leftBottom, leftTop, strokeWidth = 5f, cap = Stroke.DefaultCap)
        drawLine(colors.trackSteel, rightBottom, rightTop, strokeWidth = 5f, cap = Stroke.DefaultCap)

        // Sleepers: evenly spaced along the perspective, narrowing toward the vanishing point.
        for (i in 0 until sleeperCount) {
            val t = i / (sleeperCount - 1f)
            val y = h * (1f - t * t) // denser near the bottom, like real perspective spacing
            val progress = (h - y) / h
            val lx = leftBottom.x + (leftTop.x - leftBottom.x) * progress
            val rx = rightBottom.x + (rightTop.x - rightBottom.x) * progress
            drawLine(
                colors.trackSteelDim,
                Offset(lx - 6f, y),
                Offset(rx + 6f, y),
                strokeWidth = 4f * (1f - t * 0.6f),
            )
        }

        // Headlight streak sweeping along the track bed.
        val streakY = h * (1f - ((sweep - (-0.2f)) / 1.4f)).coerceIn(0f, 1f)
        val streakLx = leftBottom.x + (leftTop.x - leftBottom.x) * ((h - streakY) / h)
        val streakRx = rightBottom.x + (rightTop.x - rightBottom.x) * ((h - streakY) / h)
        if (streakY in 0f..h) {
            drawLine(
                brush = Brush.horizontalGradient(
                    listOf(colors.wireGlow.copy(alpha = 0f), colors.wireGlow.copy(alpha = 0.9f), colors.wireGlow.copy(alpha = 0f)),
                    startX = streakLx,
                    endX = streakRx,
                ),
                start = Offset(streakLx, streakY),
                end = Offset(streakRx, streakY),
                strokeWidth = 10f,
            )
        }
    }
}
