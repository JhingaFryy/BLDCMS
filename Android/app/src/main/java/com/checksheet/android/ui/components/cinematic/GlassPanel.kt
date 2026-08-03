package com.checksheet.android.ui.components.cinematic

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ColumnScope
import androidx.compose.material3.MaterialTheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Shape
import androidx.compose.ui.unit.dp
import com.checksheet.android.theme.RailwayTheme

/**
 * "Railway Command Center" UI overhaul: a glassmorphic container - translucent tint + a hairline
 * border over whatever [GlowBackground]/[CircuitPatternOverlay] sits behind it. Deliberately does
 * NOT use [androidx.compose.ui.draw.blur] - that modifier blurs the composable it's applied to,
 * not what's rendered behind it, so putting it on this panel would blur its own [content] (the
 * actual form fields/text), not produce a frosted-glass effect. True backdrop blur needs a
 * render-node/rendereffect technique this Compose BOM doesn't provide out of the box, so this is
 * the safe, correct approximation: a semi-transparent tint + border, same visual family as
 * glassmorphism without risking illegible blurred content.
 */
@Composable
fun GlassPanel(
    modifier: Modifier = Modifier,
    shape: Shape = MaterialTheme.shapes.extraLarge,
    content: @Composable ColumnScope.() -> Unit,
) {
    val colors = RailwayTheme.cinematicColors

    Column(
        modifier = modifier
            .clip(shape)
            .background(colors.glassTint, shape)
            .border(1.dp, colors.glassBorder, shape),
        content = content,
    )
}
