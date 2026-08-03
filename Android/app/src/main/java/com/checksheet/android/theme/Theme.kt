package com.checksheet.android.theme

import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.runtime.getValue
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.checksheet.android.ui.settings.ThemeMode
import com.checksheet.android.ui.settings.ThemeModeViewModel

/** Reach [MaterialTheme.colorScheme]-style semantic colors (success/warning) that M3 has no
 * built-in role for - see [com.checksheet.android.theme.ExtendedColors]. */
object RailwayTheme {
    val extendedColors: com.checksheet.android.theme.ExtendedColors
        @Composable get() = LocalExtendedColors.current

    /** "Railway Command Center" cinematic tokens - see [com.checksheet.android.theme.CinematicColors]. */
    val cinematicColors: com.checksheet.android.theme.CinematicColors
        @Composable get() = LocalCinematicColors.current
}

@Composable
fun ChecksheetTheme(content: @Composable () -> Unit) {
    val themeModeViewModel: ThemeModeViewModel = hiltViewModel()
    val themeMode by themeModeViewModel.themeMode.collectAsStateWithLifecycle()

    val useDarkTheme = when (themeMode) {
        ThemeMode.SYSTEM -> isSystemInDarkTheme()
        ThemeMode.LIGHT -> false
        ThemeMode.DARK -> true
    }

    val colorScheme = if (useDarkTheme) RailwayDarkColorScheme else RailwayLightColorScheme
    val extendedColors = if (useDarkTheme) DarkExtendedColors else LightExtendedColors
    val cinematicColors = if (useDarkTheme) DarkCinematicColors else LightCinematicColors

    CompositionLocalProvider(
        LocalExtendedColors provides extendedColors,
        LocalCinematicColors provides cinematicColors,
    ) {
        MaterialTheme(
            colorScheme = colorScheme,
            typography = RailwayTypography,
            shapes = RailwayShapes,
            content = content
        )
    }
}
