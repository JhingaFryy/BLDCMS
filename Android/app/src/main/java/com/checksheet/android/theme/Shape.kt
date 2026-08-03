package com.checksheet.android.theme

import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Shapes
import androidx.compose.ui.unit.dp

/** Module 31: a modern, rounded-card corner scale. `large`/`extraLarge` back most cards
 * throughout the app per the "rounded cards" design principle. */
val RailwayShapes = Shapes(
    extraSmall = RoundedCornerShape(6.dp),
    small = RoundedCornerShape(10.dp),
    medium = RoundedCornerShape(14.dp),
    large = RoundedCornerShape(20.dp),
    extraLarge = RoundedCornerShape(28.dp),
)

/** A slightly smaller radius than [RailwayShapes.large] for compact list-row cards where a
 * 20dp radius would look disproportionate (e.g. history rows, dropdown result rows). */
val CompactCardShape = RoundedCornerShape(16.dp)
