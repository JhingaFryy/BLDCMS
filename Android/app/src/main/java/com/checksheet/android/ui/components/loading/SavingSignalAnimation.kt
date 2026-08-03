package com.checksheet.android.ui.components.loading

import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.width
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import com.checksheet.android.theme.Spacing
import com.checksheet.android.ui.components.cinematic.SignalAspect
import com.checksheet.android.ui.components.cinematic.SignalLamp
import kotlinx.coroutines.delay

/**
 * "Saving" named loading animation (UI overhaul brief): a railway signal transitioning from RED
 * to GREEN. [inProgress] is the caller's own existing loading boolean (e.g.
 * `ChecksheetViewModel`'s `state.isSubmitting`) - RED while true, GREEN the instant it flips to
 * false (the caller is expected to swap this composable out for its normal success UI right
 * after, same as it previously did with a spinner). Compact size fits inline in a button; use
 * [size] to size up for the full post-submit success celebration.
 */
@Composable
fun SavingSignalAnimation(inProgress: Boolean, modifier: Modifier = Modifier, size: Dp = 24.dp, showLabel: Boolean = false) {
    val aspect = if (inProgress) SignalAspect.RED else SignalAspect.GREEN
    if (showLabel) {
        Row(modifier = modifier, verticalAlignment = Alignment.CenterVertically) {
            SignalLamp(aspect = aspect, size = size)
            Spacer(modifier = Modifier.width(Spacing.sm))
            Text(
                text = if (inProgress) "Saving checksheet..." else "Saved",
                style = MaterialTheme.typography.bodyMedium,
            )
        }
    } else {
        SignalLamp(aspect = aspect, modifier = modifier, size = size)
    }
}

/** Full-scale celebratory variant for the post-submit success screen: signal cycles RED -> AMBER
 * -> GREEN once, then holds GREEN, alongside a "Checksheet Approved for Transmission" caption. */
@Composable
fun SavingSignalCelebration(modifier: Modifier = Modifier) {
    var aspect by remember { mutableStateOf(SignalAspect.RED) }
    LaunchedEffect(Unit) {
        aspect = SignalAspect.RED
        delay(280)
        aspect = SignalAspect.AMBER
        delay(280)
        aspect = SignalAspect.GREEN
    }
    Column(modifier = modifier, horizontalAlignment = Alignment.CenterHorizontally) {
        SignalLamp(aspect = aspect, size = 64.dp)
        androidx.compose.foundation.layout.Spacer(modifier = Modifier.height(Spacing.md))
        Text(
            text = "Checksheet submitted successfully.",
            style = MaterialTheme.typography.titleMedium,
        )
    }
}
