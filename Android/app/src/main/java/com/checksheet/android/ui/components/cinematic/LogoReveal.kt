package com.checksheet.android.ui.components.cinematic

import androidx.compose.animation.core.Animatable
import androidx.compose.animation.core.CubicBezierEasing
import androidx.compose.animation.core.EaseOutCubic
import androidx.compose.animation.core.LinearEasing
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.Image
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.size
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.drawWithContent
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.BlendMode
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import com.checksheet.android.R
import com.checksheet.android.theme.RailwayTheme
import kotlinx.coroutines.delay

/** A gentle "back ease" overshoot - the logo settles very slightly past 1x scale before resting. */
private val LogoSettleEasing = CubicBezierEasing(0.34f, 1.56f, 0.64f, 1f)

/**
 * Module 47, Stage 5 (and a smaller static use on the Login screen): the official BL logo -
 * unmodified image, only animated. Scales in with a soft glow behind it, settles into a slow
 * ambient pulse, and (once, not looped) receives a diagonal metallic shine sweep. Deliberately
 * restrained per the spec ("do not overdo it") - one shine pass, a few-percent pulse, nothing that
 * competes with the logo itself.
 */
@Composable
fun LogoReveal(
    modifier: Modifier = Modifier,
    logoSize: Dp = 180.dp,
    playShineSweep: Boolean = true,
    playPulse: Boolean = true,
    onSettled: () -> Unit = {},
) {
    val colors = RailwayTheme.cinematicColors
    val scale = remember { Animatable(0.7f) }
    val imageAlpha = remember { Animatable(0f) }
    val shineProgress = remember { Animatable(-0.35f) }

    val pulseTransition = rememberInfiniteTransition(label = "logoPulse")
    val pulse by pulseTransition.animateFloat(
        initialValue = 1f,
        targetValue = if (playPulse) 1.03f else 1f,
        animationSpec = infiniteRepeatable(tween(1800, easing = LinearEasing), RepeatMode.Reverse),
        label = "logoPulseValue",
    )

    LaunchedEffect(Unit) {
        imageAlpha.animateTo(1f, tween(450))
        scale.animateTo(1f, tween(650, easing = LogoSettleEasing))
        if (playShineSweep) {
            delay(150)
            shineProgress.animateTo(1.35f, tween(750, easing = EaseOutCubic))
        }
        onSettled()
    }

    Box(modifier = modifier.size(logoSize), contentAlignment = Alignment.Center) {
        Canvas(modifier = Modifier.size(logoSize * 1.6f)) {
            drawCircle(
                brush = Brush.radialGradient(
                    colors = listOf(colors.wireGlowDim.copy(alpha = 0.45f), colors.wireGlowDim.copy(alpha = 0f)),
                ),
            )
        }

        Image(
            painter = painterResource(R.drawable.logo),
            contentDescription = "Organization Logo", // CHANGE_ME along with drawable-nodpi/logo.png for this shed's own seal
            modifier = Modifier
                .size(logoSize)
                .graphicsLayer {
                    alpha = imageAlpha.value
                    scaleX = scale.value * pulse
                    scaleY = scale.value * pulse
                }
                .drawWithContent {
                    drawContent()
                    if (playShineSweep && shineProgress.value in -0.5f..1.5f) {
                        val bandCenter = this.size.width * shineProgress.value
                        val bandWidth = this.size.width * 0.22f
                        drawRect(
                            brush = Brush.linearGradient(
                                colors = listOf(Color.Transparent, Color.White.copy(alpha = 0.35f), Color.Transparent),
                                start = Offset(bandCenter - bandWidth, 0f),
                                end = Offset(bandCenter + bandWidth, this.size.height),
                            ),
                            blendMode = BlendMode.Plus,
                        )
                    }
                },
        )
    }
}
