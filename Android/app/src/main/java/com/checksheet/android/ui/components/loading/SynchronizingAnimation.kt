package com.checksheet.android.ui.components.loading

import androidx.compose.animation.core.LinearEasing
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.unit.dp
import com.checksheet.android.theme.RailwayTheme
import com.checksheet.android.theme.Spacing
import kotlin.math.cos
import kotlin.math.sin

/**
 * "Synchronizing" named loading animation (UI overhaul brief): a small railway-network
 * visualization - a handful of "station" nodes connected by lines, with pulses of light
 * travelling along the connections. Used for [SplashScreen]'s session/`/auth/me` check
 * (`state.isLoading`) - a genuine, already-visible "connecting to the network" moment.
 */
@Composable
fun SynchronizingAnimation(label: String = "Connecting to network...", modifier: Modifier = Modifier) {
    val colors = RailwayTheme.cinematicColors
    val transition = rememberInfiniteTransition(label = "networkSync")
    val pulse by transition.animateFloat(
        initialValue = 0f,
        targetValue = 1f,
        animationSpec = infiniteRepeatable(tween(1600, easing = LinearEasing), RepeatMode.Restart),
        label = "nodePulse",
    )

    Column(modifier = modifier.fillMaxWidth().padding(Spacing.md), horizontalAlignment = Alignment.CenterHorizontally) {
        Canvas(modifier = Modifier.fillMaxWidth().height(72.dp)) {
            val w = size.width
            val h = size.height
            val centerNode = Offset(w / 2f, h / 2f)
            val outerNodes = (0 until 5).map { i ->
                val angle = (i / 5f) * 2 * Math.PI.toFloat() - Math.PI.toFloat() / 2
                Offset(
                    centerNode.x + cos(angle) * w * 0.32f,
                    centerNode.y + sin(angle) * h * 0.42f,
                )
            }

            outerNodes.forEach { node ->
                drawLine(colors.trackSteelDim, centerNode, node, strokeWidth = 1.5f)
            }

            outerNodes.forEachIndexed { i, node ->
                val t = ((pulse + i / 5f) % 1f)
                val travelPoint = Offset(
                    centerNode.x + (node.x - centerNode.x) * t,
                    centerNode.y + (node.y - centerNode.y) * t,
                )
                drawCircle(colors.wireGlow, radius = 3f, center = travelPoint)
                drawCircle(colors.trackSteel, radius = 4f, center = node)
            }

            drawCircle(colors.wireGlow, radius = 6f, center = centerNode)
        }
        Text(
            text = label,
            style = MaterialTheme.typography.bodyMedium,
            modifier = Modifier.padding(top = Spacing.xs),
        )
    }
}
