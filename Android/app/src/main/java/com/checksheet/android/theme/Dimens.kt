package com.checksheet.android.theme

import androidx.compose.ui.unit.dp

/** Module 31: one shared spacing scale so padding/gaps stay consistent across every screen
 * instead of each screen picking its own ad hoc dp values. */
object Spacing {
    val xs = 4.dp
    val sm = 8.dp
    val md = 16.dp
    val lg = 24.dp
    val xl = 32.dp
    val xxl = 48.dp
}

/** Minimum touch target size per Material 3 accessibility guidance - used for icon buttons and
 * any custom tappable row that doesn't already get this for free from a standard component. */
val MinTouchTarget = 48.dp
