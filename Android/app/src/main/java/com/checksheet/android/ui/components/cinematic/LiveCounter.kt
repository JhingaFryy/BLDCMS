package com.checksheet.android.ui.components.cinematic

import androidx.compose.animation.core.animateIntAsState
import androidx.compose.animation.core.tween
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight

/**
 * "Railway Command Center" UI overhaul: an animated count-up number. Purely presentational -
 * [value] must come from the caller's own already-existing state (e.g.
 * `HomeUiState.unreadNotificationCount`); this component never fetches or invents data itself.
 */
@Composable
fun LiveCounter(value: Int, modifier: Modifier = Modifier) {
    val animated by animateIntAsState(targetValue = value, animationSpec = tween(600), label = "liveCounter")
    Text(
        text = animated.toString(),
        style = MaterialTheme.typography.displaySmall.copy(fontFamily = FontFamily.Monospace, fontWeight = FontWeight.Bold),
        modifier = modifier,
    )
}
