package com.checksheet.android.ui.components.cinematic

import androidx.compose.animation.core.Animatable
import androidx.compose.animation.core.tween
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.alpha
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Shadow
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.checksheet.android.theme.RailwayTheme
import kotlinx.coroutines.delay

/**
 * Module 47, Stage 4: shown once [CircuitNetworkAnimation] has settled - a glowing confirmation
 * fade-in, then immediately "Proceeding to Application...". Purely presentational; the real
 * database/session check already happened via [SplashViewModel] before Stage 1 ever started.
 */
@Composable
fun DatabaseConnectedBanner(modifier: Modifier = Modifier, onFinished: () -> Unit = {}) {
    val colors = RailwayTheme.cinematicColors
    val connectedAlpha = remember { Animatable(0f) }
    val proceedingAlpha = remember { Animatable(0f) }

    LaunchedEffect(Unit) {
        connectedAlpha.animateTo(1f, tween(500))
        delay(450)
        proceedingAlpha.animateTo(1f, tween(400))
        delay(500)
        onFinished()
    }

    Column(modifier = modifier.padding(top = 8.dp)) {
        Text(
            text = "Successfully Connected to Database",
            style = MaterialTheme.typography.titleMedium.copy(
                fontWeight = FontWeight.Bold,
                color = colors.signalGreen,
                shadow = Shadow(color = colors.signalGreen.copy(alpha = 0.8f), offset = Offset.Zero, blurRadius = 18f),
            ),
            modifier = Modifier.alpha(connectedAlpha.value),
        )
        Text(
            text = "Proceeding to Application...",
            style = MaterialTheme.typography.bodyMedium.copy(color = colors.wireGlow),
            modifier = Modifier.alpha(proceedingAlpha.value).padding(top = 4.dp),
        )
    }
}
