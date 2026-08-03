package com.checksheet.android.ui.components.loading

import androidx.compose.animation.core.LinearEasing
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.tween
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.foundation.layout.Box
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
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.unit.dp
import com.checksheet.android.theme.Spacing
import com.checksheet.android.ui.components.cinematic.AnimatedTracks
import com.checksheet.android.ui.components.cinematic.LocomotiveSilhouette

/**
 * "Loading Checksheet" named loading animation (UI overhaul brief): a locomotive travelling
 * across illuminated tracks, looping. Used for the "resolving checksheet template" moment
 * ([FillChecksheetViewModel]'s `isResolvingTemplate`) - purely presentational, bound to whatever
 * boolean the caller already has; holds no loading state of its own.
 */
@Composable
fun LoadingChecksheetAnimation(label: String = "Finding checksheet template...", modifier: Modifier = Modifier) {
    val transition = rememberInfiniteTransition(label = "checksheetLoco")
    val locoX by transition.animateFloat(
        initialValue = -0.15f,
        targetValue = 1.15f,
        animationSpec = infiniteRepeatable(tween(2200, easing = LinearEasing), RepeatMode.Restart),
        label = "locoTravel",
    )

    Column(modifier = modifier.fillMaxWidth().padding(Spacing.md)) {
        Box(modifier = Modifier.fillMaxWidth().height(110.dp)) {
            AnimatedTracks(modifier = Modifier.fillMaxWidth())
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(110.dp)
                    .graphicsLayer {
                        translationX = (locoX - 0.5f) * size.width
                    },
                contentAlignment = Alignment.Center,
            ) {
                LocomotiveSilhouette()
            }
        }
        Text(
            text = label,
            style = MaterialTheme.typography.bodyMedium,
            modifier = Modifier.padding(top = Spacing.sm),
        )
    }
}
