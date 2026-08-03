package com.checksheet.android.ui.components.cinematic

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.width
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateListOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Shadow
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.checksheet.android.theme.CinematicColors
import com.checksheet.android.theme.RailwayTheme
import kotlinx.coroutines.delay

/** A single boot-log line; [showOk] marks lines that end with a glowing "[ OK ]" indicator. */
data class TerminalLine(val text: String, val showOk: Boolean = false)

/** Module 47, Stage 3's exact status sequence. */
val DefaultBootSequence = listOf(
    TerminalLine("Initializing BL-DCMS..."),
    TerminalLine("Loading system libraries...", showOk = true),
    TerminalLine("Checking application integrity...", showOk = true),
    TerminalLine("Loading configuration...", showOk = true),
    TerminalLine("Initializing secure modules...", showOk = true),
    TerminalLine("Connecting to PostgreSQL..."),
    TerminalLine("Authenticating backend...", showOk = true),
    TerminalLine("Connecting to Database...", showOk = true),
    TerminalLine("Synchronizing templates...", showOk = true),
    TerminalLine("Loading user interface...", showOk = true),
    TerminalLine("Preparing workstation...", showOk = true),
)

private data class RevealedLine(val text: String, val ok: Boolean)

/**
 * Module 47, Stage 3: monospace terminal-style status panel with a realistic per-character
 * typewriter reveal, one line at a time - never all lines at once. Purely presentational: this
 * scripted sequence has no bearing on the actual app/session state, which [SplashViewModel] alone
 * decides (see SplashScreen.kt). [onFinished] fires once every line has been revealed.
 */
@Composable
fun TerminalConsole(
    modifier: Modifier = Modifier,
    lines: List<TerminalLine> = DefaultBootSequence,
    charRevealMs: Long = 14L,
    lineGapMs: Long = 220L,
    onFinished: () -> Unit = {},
) {
    val colors = RailwayTheme.cinematicColors
    val revealed = remember { mutableStateListOf<RevealedLine>() }
    var currentPartial by remember { mutableStateOf("") }
    var currentOk by remember { mutableStateOf(false) }

    LaunchedEffect(lines) {
        for (line in lines) {
            currentPartial = ""
            currentOk = false
            for (charIndex in 1..line.text.length) {
                currentPartial = line.text.substring(0, charIndex)
                delay(charRevealMs)
            }
            if (line.showOk) {
                delay(90)
                currentOk = true
                delay(160)
            }
            revealed.add(RevealedLine(line.text, line.showOk))
            currentPartial = ""
            currentOk = false
            delay(lineGapMs)
        }
        onFinished()
    }

    Column(modifier = modifier, verticalArrangement = Arrangement.spacedBy(4.dp)) {
        revealed.forEach { line -> TerminalLineRow(line.text, line.ok, okVisible = true, colors = colors) }
        if (currentPartial.isNotEmpty()) {
            TerminalLineRow(currentPartial, showOk = true, okVisible = currentOk, colors = colors)
        }
    }
}

@Composable
private fun TerminalLineRow(text: String, showOk: Boolean, okVisible: Boolean, colors: CinematicColors) {
    Row(verticalAlignment = Alignment.CenterVertically) {
        Text(
            text = "> $text",
            fontFamily = FontFamily.Monospace,
            fontSize = 13.sp,
            color = colors.trackSteel,
            maxLines = 1,
        )
        if (showOk && okVisible) {
            Spacer(modifier = Modifier.width(8.dp))
            Text(
                text = "[ OK ]",
                fontFamily = FontFamily.Monospace,
                fontSize = 13.sp,
                fontWeight = FontWeight.Bold,
                color = colors.signalGreen,
                style = androidx.compose.ui.text.TextStyle(
                    shadow = Shadow(color = colors.signalGreen.copy(alpha = 0.85f), offset = Offset.Zero, blurRadius = 14f),
                ),
            )
        }
    }
}
