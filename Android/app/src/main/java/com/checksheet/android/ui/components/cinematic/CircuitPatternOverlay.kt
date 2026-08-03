package com.checksheet.android.ui.components.cinematic

import androidx.compose.animation.core.LinearEasing
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.drawscope.Stroke
import com.checksheet.android.theme.RailwayTheme
import kotlin.math.sin

/**
 * "Railway Command Center" UI overhaul: a faint animated circuit-board line texture, used as a
 * low-opacity overlay on top of [GlowBackground] to reinforce the "engineering" identity without
 * competing with foreground content. A handful of horizontal traces with right-angle "via" drops,
 * each pulsing opacity slightly out of phase - deliberately understated (max alpha ~0.12).
 */
@Composable
fun CircuitPatternOverlay(modifier: Modifier = Modifier, lineCount: Int = 6) {
    val colors = RailwayTheme.cinematicColors
    val transition = rememberInfiniteTransition(label = "circuitPulse")
    val phase by transition.animateFloat(
        initialValue = 0f,
        targetValue = (2 * Math.PI).toFloat(),
        animationSpec = infiniteRepeatable(tween(6000, easing = LinearEasing), RepeatMode.Restart),
        label = "circuitPhase",
    )

    Canvas(modifier = modifier.fillMaxSize()) {
        val rowHeight = size.height / (lineCount + 1)
        for (i in 1..lineCount) {
            val y = rowHeight * i
            val pulse = 0.06f + 0.06f * ((sin(phase + i) + 1f) / 2f)
            val strokeColor = colors.circuitLine.copy(alpha = pulse)
            val xStart = size.width * (0.05f + 0.03f * (i % 3))
            val xEnd = size.width * (0.55f + 0.4f * ((i * 7) % 5) / 5f)
            val viaX = xStart + (xEnd - xStart) * 0.7f

            drawLine(strokeColor, Offset(xStart, y), Offset(viaX, y), strokeWidth = 2f, cap = Stroke.DefaultCap)
            drawLine(strokeColor, Offset(viaX, y), Offset(viaX, y - rowHeight * 0.35f), strokeWidth = 2f)
            drawLine(strokeColor, Offset(viaX, y - rowHeight * 0.35f), Offset(xEnd, y - rowHeight * 0.35f), strokeWidth = 2f)
            drawCircle(strokeColor, radius = 4f, center = Offset(viaX, y))
        }
    }
}
