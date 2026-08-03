package com.checksheet.android.ui.components.cinematic

import androidx.compose.animation.core.LinearEasing
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.width
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.drawscope.Fill
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import com.checksheet.android.theme.RailwayTheme

/**
 * "Railway Command Center" UI overhaul: an ORIGINAL stylized electric-locomotive silhouette -
 * boxy body, sloped nose, raised cab window band, and a pantograph on the roof - proportioned in
 * the general spirit of an Indian Railways electric loco (WAP-7/WAG-9HC class) without tracing or
 * reproducing any specific copyrighted artwork/photo. Pure geometric [Path] construction, flat-
 * filled silhouette + glowing outline, with a slow pantograph-spark pulse. Decorative only.
 */
@Composable
fun LocomotiveSilhouette(modifier: Modifier = Modifier, width: Dp = 220.dp, height: Dp = 110.dp) {
    val colors = RailwayTheme.cinematicColors
    val transition = rememberInfiniteTransition(label = "locoSpark")
    val sparkPulse by transition.animateFloat(
        initialValue = 0.3f,
        targetValue = 1f,
        animationSpec = infiniteRepeatable(tween(900, easing = LinearEasing), RepeatMode.Reverse),
        label = "pantographSpark",
    )

    Canvas(modifier = modifier.width(width).height(height)) {
        val w = size.width
        val h = size.height
        val bodyTop = h * 0.32f
        val bodyBottom = h * 0.82f
        val noseStart = w * 0.78f

        val body = Path().apply {
            moveTo(0f, bodyBottom)
            lineTo(0f, bodyTop + h * 0.06f)
            // Slight roof curve down to the body.
            quadraticTo(w * 0.04f, bodyTop, w * 0.14f, bodyTop)
            lineTo(noseStart, bodyTop)
            // Sloped aerodynamic nose.
            quadraticTo(w * 0.96f, bodyTop + h * 0.05f, w, h * 0.58f)
            lineTo(w, bodyBottom)
            close()
        }

        // Underframe / bogies.
        val underframe = Path().apply {
            moveTo(w * 0.04f, bodyBottom)
            lineTo(w * 0.96f, bodyBottom)
            lineTo(w * 0.92f, h * 0.92f)
            lineTo(w * 0.08f, h * 0.92f)
            close()
        }

        drawPath(underframe, color = colors.trackSteelDim, style = Fill)
        drawPath(body, color = colors.trackSteel, style = Fill)
        drawPath(body, color = colors.wireGlow.copy(alpha = 0.55f), style = Stroke(width = 2.5f))

        // Cab window band.
        val windowBand = Path().apply {
            moveTo(w * 0.18f, bodyTop + h * 0.09f)
            lineTo(noseStart - w * 0.02f, bodyTop + h * 0.09f)
            lineTo(noseStart - w * 0.08f, bodyTop + h * 0.2f)
            lineTo(w * 0.2f, bodyTop + h * 0.2f)
            close()
        }
        drawPath(windowBand, color = colors.wireGlow.copy(alpha = 0.85f), style = Fill)

        // Wheels.
        val wheelRadius = h * 0.07f
        val wheelY = h * 0.92f
        listOf(0.18f, 0.36f, 0.62f, 0.8f).forEach { fx ->
            drawCircle(colors.trackSteelDim, radius = wheelRadius, center = Offset(w * fx, wheelY))
            drawCircle(colors.wireGlowDim, radius = wheelRadius * 0.35f, center = Offset(w * fx, wheelY))
        }

        // Pantograph: a simple diamond/zigzag arm reaching up from the roof, with a pulsing spark
        // where it (implicitly) meets the overhead wire above the canvas bounds.
        val pantoBaseX = w * 0.42f
        val pantoBaseY = bodyTop
        val pantoTopY = 0f
        val pantoPath = Path().apply {
            moveTo(pantoBaseX - w * 0.05f, pantoBaseY)
            lineTo(pantoBaseX, pantoTopY + h * 0.08f)
            lineTo(pantoBaseX + w * 0.05f, pantoBaseY)
        }
        drawPath(pantoPath, color = colors.trackSteel, style = Stroke(width = 2f))
        drawCircle(
            color = colors.wireGlow.copy(alpha = sparkPulse),
            radius = 5f + 3f * sparkPulse,
            center = Offset(pantoBaseX, pantoTopY + h * 0.08f),
        )
    }
}
