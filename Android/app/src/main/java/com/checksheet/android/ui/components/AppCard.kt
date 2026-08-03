package com.checksheet.android.ui.components

import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.tween
import androidx.compose.foundation.clickable
import androidx.compose.foundation.interaction.MutableInteractionSource
import androidx.compose.foundation.interaction.collectIsPressedAsState
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ColumnScope
import androidx.compose.material.ripple.rememberRipple
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.contentColorFor
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Shape
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp

/**
 * A rounded, elevated card with a subtle press animation (slight scale-down + elevation change) -
 * the "Card elevation on touch" micro-interaction from Module 31's spec. When [onClick] is null
 * this is a static, non-interactive card (still gets the rounded/elevated styling, just no press
 * feedback). Duration is short (120ms) per the module's "avoid oversized/long transitions" rule.
 */
@Composable
fun AppCard(
    modifier: Modifier = Modifier,
    onClick: (() -> Unit)? = null,
    shape: Shape = MaterialTheme.shapes.large,
    containerColor: Color = MaterialTheme.colorScheme.surface,
    contentColor: Color = contentColorFor(containerColor),
    tonalElevation: Dp = 1.dp,
    pressedTonalElevation: Dp = 4.dp,
    content: @Composable ColumnScope.() -> Unit,
) {
    val interactionSource = remember { MutableInteractionSource() }
    val isPressed by interactionSource.collectIsPressedAsState()
    val scale by animateFloatAsState(
        targetValue = if (isPressed && onClick != null) 0.98f else 1f,
        animationSpec = tween(120),
        label = "cardPressScale",
    )
    val elevation by animateFloatAsState(
        targetValue = if (isPressed && onClick != null) pressedTonalElevation.value else tonalElevation.value,
        animationSpec = tween(120),
        label = "cardPressElevation",
    )

    Surface(
        modifier = modifier
            .graphicsLayer { scaleX = scale; scaleY = scale }
            .then(
                if (onClick != null) {
                    Modifier.clickable(
                        interactionSource = interactionSource,
                        indication = rememberRipple(),
                        onClick = onClick,
                    )
                } else Modifier
            ),
        shape = shape,
        color = containerColor,
        contentColor = contentColor,
        tonalElevation = elevation.dp,
        shadowElevation = (elevation / 2f).dp,
    ) {
        Column(content = content)
    }
}
