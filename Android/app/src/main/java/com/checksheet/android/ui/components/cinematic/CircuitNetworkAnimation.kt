package com.checksheet.android.ui.components.cinematic

import androidx.compose.animation.core.Animatable
import androidx.compose.animation.core.LinearEasing
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateListOf
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.drawscope.Stroke
import com.checksheet.android.theme.RailwayTheme
import kotlinx.coroutines.delay
import kotlin.math.ceil
import kotlin.math.sin
import kotlin.math.sqrt
import kotlin.random.Random

private data class CircuitEdge(val from: Int, val to: Int)

/**
 * Module 47, Stage 1+2: a PCB-style node network on a faint grid with drifting ambient particles.
 * Nodes start red (disconnected); a scripted sequence lights up traces one at a time - a bright
 * sweep travels from one endpoint to the other, then both nodes flip to railway green with a soft
 * glow. Node layout and edges are computed once (`remember`), never re-randomized on recomposition
 * - only the activation sequence advances over time. `onSettled` fires once the scripted sequence
 * finishes, so the caller (SplashScreen) knows when to move to the next stage; this component owns
 * no navigation/business state of its own.
 */
@Composable
fun CircuitNetworkAnimation(
    modifier: Modifier = Modifier,
    nodeCount: Int = 18,
    activationIntervalMs: Long = 200L,
    completionFraction: Float = 0.85f,
    onSettled: () -> Unit = {},
) {
    val colors = RailwayTheme.cinematicColors

    // Jittered grid layout so nodes spread evenly across the screen without overlapping.
    val nodePositions = remember(nodeCount) {
        val cols = ceil(sqrt(nodeCount.toDouble())).toInt()
        val rows = ceil(nodeCount / cols.toDouble()).toInt()
        val rnd = Random(nodeCount * 7919)
        (0 until nodeCount).map { i ->
            val col = i % cols
            val row = i / cols
            val jitterX = (rnd.nextFloat() - 0.5f) * (1f / cols) * 0.6f
            val jitterY = (rnd.nextFloat() - 0.5f) * (1f / rows) * 0.6f
            Offset(
                x = ((col + 0.5f) / cols + jitterX).coerceIn(0.05f, 0.95f),
                y = ((row + 0.5f) / rows + jitterY).coerceIn(0.10f, 0.80f),
            )
        }
    }

    // Nearest-neighbor edges (2 per node, deduped) - a sparse PCB-like mesh, not a full graph.
    val edges = remember(nodePositions) {
        val result = LinkedHashSet<CircuitEdge>()
        nodePositions.indices.forEach { i ->
            val nearest = nodePositions.indices.filter { it != i }
                .sortedBy { j ->
                    val dx = nodePositions[i].x - nodePositions[j].x
                    val dy = nodePositions[i].y - nodePositions[j].y
                    dx * dx + dy * dy
                }
                .take(2)
            nearest.forEach { j ->
                result.add(if (i < j) CircuitEdge(i, j) else CircuitEdge(j, i))
            }
        }
        result.toList()
    }

    val activationOrder = remember(edges) { edges.indices.shuffled(Random(edges.size * 104729 + 1)) }
    val activatedCount = (edges.size * completionFraction).toInt().coerceIn(0, edges.size)
    val edgeProgress = remember(edges) { edges.map { Animatable(0f) } }
    val connectedNodes = remember { mutableStateListOf<Int>() }

    LaunchedEffect(edges) {
        for (edgeIndex in activationOrder.take(activatedCount)) {
            val edge = edges[edgeIndex]
            edgeProgress[edgeIndex].animateTo(1f, tween(260, easing = LinearEasing))
            if (edge.from !in connectedNodes) connectedNodes.add(edge.from)
            if (edge.to !in connectedNodes) connectedNodes.add(edge.to)
            delay(activationIntervalMs)
        }
        onSettled()
    }

    val ambientTransition = rememberInfiniteTransition(label = "circuitAmbient")
    val ambientPhase by ambientTransition.animateFloat(
        initialValue = 0f,
        targetValue = (2 * Math.PI).toFloat(),
        animationSpec = infiniteRepeatable(tween(9000, easing = LinearEasing), RepeatMode.Restart),
        label = "circuitAmbientPhase",
    )

    Canvas(modifier = modifier.fillMaxSize()) {
        // Faint background grid.
        val gridSpacing = 48f
        var gx = 0f
        while (gx < size.width) {
            drawLine(colors.circuitLine.copy(alpha = 0.05f), Offset(gx, 0f), Offset(gx, size.height), strokeWidth = 1f)
            gx += gridSpacing
        }
        var gy = 0f
        while (gy < size.height) {
            drawLine(colors.circuitLine.copy(alpha = 0.05f), Offset(0f, gy), Offset(size.width, gy), strokeWidth = 1f)
            gy += gridSpacing
        }

        // Slow-drifting ambient particles, independent of the activation sequence.
        repeat(10) { i ->
            val px = size.width * ((i * 0.093f + (sin(ambientPhase + i) + 1f) * 0.05f) % 1f)
            val py = size.height * ((i * 0.211f + (sin(ambientPhase * 0.7f + i * 1.7f) + 1f) * 0.04f) % 1f)
            drawCircle(colors.wireGlowDim.copy(alpha = 0.18f), radius = 3f, center = Offset(px, py))
        }

        // Traces, with a traveling current-flow sweep while each one is still animating in.
        edges.forEachIndexed { index, edge ->
            val p0 = Offset(nodePositions[edge.from].x * size.width, nodePositions[edge.from].y * size.height)
            val p1 = Offset(nodePositions[edge.to].x * size.width, nodePositions[edge.to].y * size.height)
            val progress = edgeProgress[index].value
            if (progress <= 0f) {
                drawLine(colors.trackSteelDim.copy(alpha = 0.25f), p0, p1, strokeWidth = 1.5f)
            } else {
                drawLine(colors.wireGlow.copy(alpha = 0.9f), p0, p1, strokeWidth = 2.5f, cap = Stroke.DefaultCap)
                if (progress < 1f) {
                    val sweepPoint = Offset(
                        x = p0.x + (p1.x - p0.x) * progress,
                        y = p0.y + (p1.y - p0.y) * progress,
                    )
                    drawCircle(colors.wireGlow, radius = 5f, center = sweepPoint)
                }
            }
        }

        // Nodes: red until connected, then green with a soft glow.
        nodePositions.forEachIndexed { index, fraction ->
            val center = Offset(fraction.x * size.width, fraction.y * size.height)
            val isConnected = index in connectedNodes
            val baseColor = if (isConnected) colors.signalGreen else colors.signalRed
            drawCircle(baseColor.copy(alpha = 0.25f), radius = 14f, center = center)
            drawCircle(baseColor, radius = 6f, center = center)
        }
    }
}
