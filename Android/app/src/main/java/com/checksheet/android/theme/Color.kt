package com.checksheet.android.theme

import androidx.compose.material3.ColorScheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Immutable
import androidx.compose.runtime.staticCompositionLocalOf
import androidx.compose.ui.graphics.Color

/**
 * Module 31: Deep Railway Blue / Steel Grey / Safety Orange industrial palette. Material 3's
 * [ColorScheme] has no built-in "success"/"warning" roles - those live in [ExtendedColors]
 * instead (see the CompositionLocal below), keeping the same tonal pattern (base/onBase/
 * container/onContainer) M3 already uses for primary/secondary/tertiary/error so every role
 * behaves consistently wherever it's consumed.
 */

// --- Light scheme ---
private val PrimaryLight = Color(0xFF0D47A1) // Deep Railway Blue
private val OnPrimaryLight = Color(0xFFFFFFFF)
private val PrimaryContainerLight = Color(0xFFD6E3FF)
private val OnPrimaryContainerLight = Color(0xFF001B3D)

private val SecondaryLight = Color(0xFF546E7A) // Steel Grey
private val OnSecondaryLight = Color(0xFFFFFFFF)
private val SecondaryContainerLight = Color(0xFFCFD8DC)
private val OnSecondaryContainerLight = Color(0xFF1C2B30)

private val TertiaryLight = Color(0xFFE65100) // Safety Orange (accent)
private val OnTertiaryLight = Color(0xFFFFFFFF)
private val TertiaryContainerLight = Color(0xFFFFDBC2)
private val OnTertiaryContainerLight = Color(0xFF3E1500)

private val ErrorLight = Color(0xFFB3261E) // Material Red
private val OnErrorLight = Color(0xFFFFFFFF)
private val ErrorContainerLight = Color(0xFFF9DEDC)
private val OnErrorContainerLight = Color(0xFF410E0B)

private val BackgroundLight = Color(0xFFF7F8FA) // Light Grey / White
private val OnBackgroundLight = Color(0xFF1A1C1E)
private val SurfaceLight = Color(0xFFF7F8FA)
private val OnSurfaceLight = Color(0xFF1A1C1E)
private val SurfaceVariantLight = Color(0xFFE1E4E9)
private val OnSurfaceVariantLight = Color(0xFF44474E)
private val SurfaceContainerLowLight = Color(0xFFF1F2F5)
private val SurfaceContainerLight = Color(0xFFEBEDF1)
private val SurfaceContainerHighLight = Color(0xFFE5E8EC)
private val OutlineLight = Color(0xFF74777F)
private val OutlineVariantLight = Color(0xFFC4C7CE)

// --- Dark scheme ---
private val PrimaryDark = Color(0xFF9DC2FF)
private val OnPrimaryDark = Color(0xFF00315C)
private val PrimaryContainerDark = Color(0xFF0D47A1)
private val OnPrimaryContainerDark = Color(0xFFD6E3FF)

private val SecondaryDark = Color(0xFFB0BEC5)
private val OnSecondaryDark = Color(0xFF263238)
private val SecondaryContainerDark = Color(0xFF37474F)
private val OnSecondaryContainerDark = Color(0xFFCFD8DC)

private val TertiaryDark = Color(0xFFFFB77C)
private val OnTertiaryDark = Color(0xFF4A2600)
private val TertiaryContainerDark = Color(0xFFE65100)
private val OnTertiaryContainerDark = Color(0xFFFFDBC2)

private val ErrorDark = Color(0xFFF2B8B5)
private val OnErrorDark = Color(0xFF601410)
private val ErrorContainerDark = Color(0xFF8C1D18)
private val OnErrorContainerDark = Color(0xFFF9DEDC)

private val BackgroundDark = Color(0xFF121417)
private val OnBackgroundDark = Color(0xFFE2E2E6)
private val SurfaceDark = Color(0xFF121417)
private val OnSurfaceDark = Color(0xFFE2E2E6)
private val SurfaceVariantDark = Color(0xFF43474E)
private val OnSurfaceVariantDark = Color(0xFFC4C6CF)
private val SurfaceContainerLowDark = Color(0xFF1A1C1F)
private val SurfaceContainerDark = Color(0xFF1E2023)
private val SurfaceContainerHighDark = Color(0xFF282A2E)
private val OutlineDark = Color(0xFF8D9199)
private val OutlineVariantDark = Color(0xFF43474E)

val RailwayLightColorScheme: ColorScheme = lightColorScheme(
    primary = PrimaryLight,
    onPrimary = OnPrimaryLight,
    primaryContainer = PrimaryContainerLight,
    onPrimaryContainer = OnPrimaryContainerLight,
    secondary = SecondaryLight,
    onSecondary = OnSecondaryLight,
    secondaryContainer = SecondaryContainerLight,
    onSecondaryContainer = OnSecondaryContainerLight,
    tertiary = TertiaryLight,
    onTertiary = OnTertiaryLight,
    tertiaryContainer = TertiaryContainerLight,
    onTertiaryContainer = OnTertiaryContainerLight,
    error = ErrorLight,
    onError = OnErrorLight,
    errorContainer = ErrorContainerLight,
    onErrorContainer = OnErrorContainerLight,
    background = BackgroundLight,
    onBackground = OnBackgroundLight,
    surface = SurfaceLight,
    onSurface = OnSurfaceLight,
    surfaceVariant = SurfaceVariantLight,
    onSurfaceVariant = OnSurfaceVariantLight,
    surfaceContainerLow = SurfaceContainerLowLight,
    surfaceContainer = SurfaceContainerLight,
    surfaceContainerHigh = SurfaceContainerHighLight,
    outline = OutlineLight,
    outlineVariant = OutlineVariantLight,
)

val RailwayDarkColorScheme: ColorScheme = darkColorScheme(
    primary = PrimaryDark,
    onPrimary = OnPrimaryDark,
    primaryContainer = PrimaryContainerDark,
    onPrimaryContainer = OnPrimaryContainerDark,
    secondary = SecondaryDark,
    onSecondary = OnSecondaryDark,
    secondaryContainer = SecondaryContainerDark,
    onSecondaryContainer = OnSecondaryContainerDark,
    tertiary = TertiaryDark,
    onTertiary = OnTertiaryDark,
    tertiaryContainer = TertiaryContainerDark,
    onTertiaryContainer = OnTertiaryContainerDark,
    error = ErrorDark,
    onError = OnErrorDark,
    errorContainer = ErrorContainerDark,
    onErrorContainer = OnErrorContainerDark,
    background = BackgroundDark,
    onBackground = OnBackgroundDark,
    surface = SurfaceDark,
    onSurface = OnSurfaceDark,
    surfaceVariant = SurfaceVariantDark,
    onSurfaceVariant = OnSurfaceVariantDark,
    surfaceContainerLow = SurfaceContainerLowDark,
    surfaceContainer = SurfaceContainerDark,
    surfaceContainerHigh = SurfaceContainerHighDark,
    outline = OutlineDark,
    outlineVariant = OutlineVariantDark,
)

/** Semantic colors M3's [ColorScheme] has no slot for - Railway Green (success) and Amber
 * (warning) - exposed the same way [MaterialTheme.colorScheme] is, via [LocalExtendedColors]. */
@Immutable
data class ExtendedColors(
    val success: Color,
    val onSuccess: Color,
    val successContainer: Color,
    val onSuccessContainer: Color,
    val warning: Color,
    val onWarning: Color,
    val warningContainer: Color,
    val onWarningContainer: Color,
)

val LightExtendedColors = ExtendedColors(
    success = Color(0xFF2E7D32),
    onSuccess = Color(0xFFFFFFFF),
    successContainer = Color(0xFFC8E6C9),
    onSuccessContainer = Color(0xFF1B5E20),
    warning = Color(0xFFB05B00),
    onWarning = Color(0xFFFFFFFF),
    warningContainer = Color(0xFFFFECB3),
    onWarningContainer = Color(0xFF7A4A00),
)

val DarkExtendedColors = ExtendedColors(
    success = Color(0xFF8BC98F),
    onSuccess = Color(0xFF0F3D12),
    successContainer = Color(0xFF1B5E20),
    onSuccessContainer = Color(0xFFC8E6C9),
    warning = Color(0xFFFFC46B),
    onWarning = Color(0xFF4A2E00),
    warningContainer = Color(0xFF7A4A00),
    onWarningContainer = Color(0xFFFFECB3),
)

val LocalExtendedColors = staticCompositionLocalOf { LightExtendedColors }

/**
 * "Railway Command Center" cinematic palette (UI/UX overhaul module) - purely presentational
 * tokens for the new animated backgrounds, glass panels, and railway-signal/OHE-wire artwork.
 * Deliberately a SEPARATE CompositionLocal from [ExtendedColors]/[MaterialTheme.colorScheme]
 * (same pattern, new slot) rather than repurposing existing M3 roles, so no existing screen's
 * colors change - only screens explicitly redesigned in this module read [RailwayTheme.cinematicColors].
 */
@Immutable
data class CinematicColors(
    val voidTop: Color,
    val voidBottom: Color,
    val wireGlow: Color,
    val wireGlowDim: Color,
    val signalRed: Color,
    val signalAmber: Color,
    val signalGreen: Color,
    val trackSteel: Color,
    val trackSteelDim: Color,
    val glassTint: Color,
    val glassBorder: Color,
    val circuitLine: Color,
    val blueprintLine: Color,
)

val DarkCinematicColors = CinematicColors(
    voidTop = Color(0xFF0A1220),
    voidBottom = Color(0xFF03050A),
    wireGlow = Color(0xFF6FE3FF),
    wireGlowDim = Color(0xFF1C4A57),
    signalRed = Color(0xFFFF3B30),
    signalAmber = Color(0xFFFFB400),
    signalGreen = Color(0xFF33E084),
    trackSteel = Color(0xFF8C97A6),
    trackSteelDim = Color(0xFF3A4250),
    glassTint = Color(0x33101820),
    glassBorder = Color(0x40FFFFFF),
    circuitLine = Color(0x2E6FE3FF),
    blueprintLine = Color(0xFF9DC2FF),
)

val LightCinematicColors = CinematicColors(
    voidTop = Color(0xFFE9EEF7),
    voidBottom = Color(0xFFCBD6E6),
    wireGlow = Color(0xFF0B7285),
    wireGlowDim = Color(0xFFAFD9E2),
    signalRed = Color(0xFFC62828),
    signalAmber = Color(0xFFB05B00),
    signalGreen = Color(0xFF1B7A43),
    trackSteel = Color(0xFF546E7A),
    trackSteelDim = Color(0xFFB9C4CC),
    glassTint = Color(0x40FFFFFF),
    glassBorder = Color(0x40001B3D),
    circuitLine = Color(0x2B0D47A1),
    blueprintLine = Color(0xFF0D47A1),
)

val LocalCinematicColors = staticCompositionLocalOf { DarkCinematicColors }
