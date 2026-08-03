package com.checksheet.android.ui.components

import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.widthIn
import androidx.compose.material3.windowsizeclass.ExperimentalMaterial3WindowSizeClassApi
import androidx.compose.material3.windowsizeclass.WindowSizeClass
import androidx.compose.material3.windowsizeclass.WindowWidthSizeClass
import androidx.compose.runtime.Composable
import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.runtime.ProvidableCompositionLocal
import androidx.compose.runtime.staticCompositionLocalOf
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.DpSize
import androidx.compose.ui.unit.dp

/**
 * Module 31: the app's [WindowSizeClass], computed once in MainActivity from the Activity's
 * window metrics and provided down the whole composition - screens read this instead of each
 * computing their own size-class breakpoints. Defaults to a Compact/phone class so Previews and
 * any composable outside MainActivity's provider still render sensibly.
 */
@OptIn(ExperimentalMaterial3WindowSizeClassApi::class)
val LocalWindowSizeClass: ProvidableCompositionLocal<WindowSizeClass> = staticCompositionLocalOf {
    WindowSizeClass.calculateFromSize(DpSize(360.dp, 800.dp))
}

/**
 * Wraps a single-column, form-like screen (Login, OTP, Profile, Settings, ...) so it stays a
 * comfortable reading width on large phones/tablets/landscape instead of stretching edge to edge.
 * Phones in portrait (Compact width) are unaffected - content still fills the full width there.
 */
@OptIn(ExperimentalMaterial3WindowSizeClassApi::class)
@Composable
fun ResponsiveContainer(
    modifier: Modifier = Modifier,
    maxContentWidth: androidx.compose.ui.unit.Dp = 560.dp,
    content: @Composable () -> Unit,
) {
    val windowSizeClass = LocalWindowSizeClass.current
    val isWide = windowSizeClass.widthSizeClass != WindowWidthSizeClass.Compact

    if (isWide) {
        Box(modifier = modifier.fillMaxSize(), contentAlignment = Alignment.TopCenter) {
            Box(modifier = Modifier.widthIn(max = maxContentWidth)) {
                content()
            }
        }
    } else {
        Box(modifier = modifier.fillMaxWidth()) {
            content()
        }
    }
}

@OptIn(ExperimentalMaterial3WindowSizeClassApi::class)
@Composable
fun ProvideWindowSizeClass(windowSizeClass: WindowSizeClass, content: @Composable () -> Unit) {
    CompositionLocalProvider(LocalWindowSizeClass provides windowSizeClass, content = content)
}
