package com.checksheet.android.ui.components.loading

import androidx.compose.animation.core.LinearEasing
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import com.checksheet.android.theme.RailwayTheme
import com.checksheet.android.theme.Spacing

/**
 * "Generating PDF" named loading animation (UI overhaul brief): a blueprint-style document
 * outline that draws itself on in a loop (page border + a few "text line" strokes revealing left
 * to right). Used for [ChecksheetDetailScreen]/[HistoryScreen]'s PDF download-in-progress states
 * (`isPdfBusy`/`pdfBusy`) - inline-compact size fits the small button context those screens use.
 */
@Composable
fun GeneratingPdfAnimation(modifier: Modifier = Modifier, size: Dp = 22.dp, showLabel: Boolean = false) {
    val colors = RailwayTheme.cinematicColors
    val transition = rememberInfiniteTransition(label = "pdfBlueprint")
    val reveal by transition.animateFloat(
        initialValue = 0f,
        targetValue = 1f,
        animationSpec = infiniteRepeatable(tween(1100, easing = LinearEasing), RepeatMode.Restart),
        label = "blueprintReveal",
    )

    if (showLabel) {
        Row(verticalAlignment = Alignment.CenterVertically, modifier = modifier) {
            BlueprintCanvas(reveal, colors.blueprintLine, size)
            Spacer(modifier = Modifier.width(Spacing.sm))
            Text("Generating PDF...", style = MaterialTheme.typography.bodyMedium)
        }
    } else {
        BlueprintCanvas(reveal, colors.blueprintLine, size, modifier)
    }
}

@Composable
private fun BlueprintCanvas(reveal: Float, lineColor: androidx.compose.ui.graphics.Color, size: Dp, modifier: Modifier = Modifier) {
    Canvas(modifier = modifier.size(size)) {
        val w = this.size.width
        val h = this.size.height
        val margin = w * 0.12f

        // Page border.
        drawRect(
            color = lineColor,
            topLeft = Offset(margin, margin * 0.6f),
            size = androidx.compose.ui.geometry.Size(w - margin * 2, h - margin * 1.2f),
            style = Stroke(width = 1.6f),
        )

        // Three "text lines" that draw on left-to-right, staggered, looping with `reveal`.
        val lineYs = listOf(0.38f, 0.58f, 0.78f)
        lineYs.forEachIndexed { i, fy ->
            val lineProgress = ((reveal - i * 0.15f).mod(1f)).coerceIn(0f, 1f)
            val y = h * fy
            val xStart = margin * 1.6f
            val xEndFull = w - margin * 1.6f
            val xEnd = xStart + (xEndFull - xStart) * lineProgress
            drawLine(lineColor, Offset(xStart, y), Offset(xEnd, y), strokeWidth = 1.4f)
        }
    }
}
