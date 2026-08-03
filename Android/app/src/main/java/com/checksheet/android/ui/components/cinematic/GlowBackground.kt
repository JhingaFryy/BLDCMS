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
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.drawscope.drawIntoCanvas
import com.checksheet.android.theme.RailwayTheme

/**
 * "Railway Command Center" UI overhaul: a slow-drifting radial gradient mesh used as the base
 * background layer on Splash/Login/OTP/Home. Purely decorative - a single [Canvas] draw, no
 * state beyond the animation clock, safe to drop behind any screen's existing content without
 * touching that content's own state or logic.
 */
@Composable
fun GlowBackground(modifier: Modifier = Modifier) {
    val colors = RailwayTheme.cinematicColors
    val transition = rememberInfiniteTransition(label = "glowBackground")
    val drift by transition.animateFloat(
        initialValue = 0f,
        targetValue = 1f,
        animationSpec = infiniteRepeatable(tween(14000, easing = LinearEasing), RepeatMode.Reverse),
        label = "glowDrift",
    )

    Canvas(modifier = modifier.fillMaxSize()) {
        drawRect(
            brush = Brush.verticalGradient(
                colors = listOf(colors.voidTop, colors.voidBottom),
            ),
        )

        val cx = size.width * (0.2f + 0.6f * drift)
        val cy = size.height * 0.15f
        drawIntoCanvas {
            drawCircle(
                brush = Brush.radialGradient(
                    colors = listOf(colors.wireGlowDim.copy(alpha = 0.35f), colors.wireGlowDim.copy(alpha = 0f)),
                    center = Offset(cx, cy),
                    radius = size.maxDimension * 0.6f,
                ),
                radius = size.maxDimension * 0.6f,
                center = Offset(cx, cy),
            )
        }

        val cx2 = size.width * (0.85f - 0.5f * drift)
        val cy2 = size.height * 0.85f
        drawCircle(
            brush = Brush.radialGradient(
                colors = listOf(colors.wireGlowDim.copy(alpha = 0.25f), colors.wireGlowDim.copy(alpha = 0f)),
                center = Offset(cx2, cy2),
                radius = size.maxDimension * 0.5f,
            ),
            radius = size.maxDimension * 0.5f,
            center = Offset(cx2, cy2),
        )
    }
}
