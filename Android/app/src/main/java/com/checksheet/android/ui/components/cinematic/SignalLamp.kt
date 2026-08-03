package com.checksheet.android.ui.components.cinematic

import androidx.compose.animation.animateColorAsState
import androidx.compose.animation.core.tween
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.layout.size
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import com.checksheet.android.theme.RailwayTheme

enum class SignalAspect { RED, AMBER, GREEN }

/**
 * "Railway Command Center" UI overhaul: a single railway signal lamp that animates its color
 * between [SignalAspect]s (real signal colors, from [RailwayTheme.cinematicColors]) with a soft
 * glow halo. Used both as a small inline "saving" indicator (RED while in flight, GREEN on
 * success) and as the centerpiece of the full-scale saving/success animation. The [aspect] is
 * driven entirely by the caller's existing loading/success state - this component holds no
 * business state of its own.
 */
@Composable
fun SignalLamp(aspect: SignalAspect, modifier: Modifier = Modifier, size: Dp = 24.dp) {
    val colors = RailwayTheme.cinematicColors
    val target = when (aspect) {
        SignalAspect.RED -> colors.signalRed
        SignalAspect.AMBER -> colors.signalAmber
        SignalAspect.GREEN -> colors.signalGreen
    }
    val lampColor by animateColorAsState(targetValue = target, animationSpec = tween(450), label = "signalAspect")

    Canvas(modifier = modifier.size(size)) {
        val radius = this.size.minDimension / 2f
        drawCircle(
            brush = Brush.radialGradient(
                listOf(lampColor.copy(alpha = 0.55f), lampColor.copy(alpha = 0f)),
            ),
            radius = radius,
        )
        drawCircle(color = lampColor, radius = radius * 0.55f)
        drawCircle(color = lampColor.copy(alpha = 0.9f), radius = radius * 0.3f)
    }
}
