package com.checksheet.android.theme

import androidx.compose.material3.Typography
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.sp

/**
 * Module 31: full Material 3 type scale, tuned for an industrial field-use app read at arm's
 * length - titles are a touch heavier (SemiBold) for scannability, body text stays at or above
 * 14sp, and line heights are slightly generous for readability over pure density. No custom font
 * asset is bundled, so this uses the platform default sans-serif family throughout.
 */
private val RailwayFontFamily = FontFamily.Default

val RailwayTypography = Typography(
    displayLarge = TextStyle(
        fontFamily = RailwayFontFamily, fontWeight = FontWeight.Bold,
        fontSize = 57.sp, lineHeight = 64.sp, letterSpacing = (-0.25).sp,
    ),
    displayMedium = TextStyle(
        fontFamily = RailwayFontFamily, fontWeight = FontWeight.Bold,
        fontSize = 45.sp, lineHeight = 52.sp, letterSpacing = 0.sp,
    ),
    displaySmall = TextStyle(
        fontFamily = RailwayFontFamily, fontWeight = FontWeight.SemiBold,
        fontSize = 36.sp, lineHeight = 44.sp, letterSpacing = 0.sp,
    ),
    headlineLarge = TextStyle(
        fontFamily = RailwayFontFamily, fontWeight = FontWeight.SemiBold,
        fontSize = 32.sp, lineHeight = 40.sp, letterSpacing = 0.sp,
    ),
    headlineMedium = TextStyle(
        fontFamily = RailwayFontFamily, fontWeight = FontWeight.SemiBold,
        fontSize = 28.sp, lineHeight = 36.sp, letterSpacing = 0.sp,
    ),
    headlineSmall = TextStyle(
        fontFamily = RailwayFontFamily, fontWeight = FontWeight.SemiBold,
        fontSize = 24.sp, lineHeight = 32.sp, letterSpacing = 0.sp,
    ),
    titleLarge = TextStyle(
        fontFamily = RailwayFontFamily, fontWeight = FontWeight.SemiBold,
        fontSize = 22.sp, lineHeight = 28.sp, letterSpacing = 0.sp,
    ),
    titleMedium = TextStyle(
        fontFamily = RailwayFontFamily, fontWeight = FontWeight.SemiBold,
        fontSize = 17.sp, lineHeight = 24.sp, letterSpacing = 0.15.sp,
    ),
    titleSmall = TextStyle(
        fontFamily = RailwayFontFamily, fontWeight = FontWeight.Medium,
        fontSize = 15.sp, lineHeight = 20.sp, letterSpacing = 0.1.sp,
    ),
    bodyLarge = TextStyle(
        fontFamily = RailwayFontFamily, fontWeight = FontWeight.Normal,
        fontSize = 16.sp, lineHeight = 24.sp, letterSpacing = 0.15.sp,
    ),
    bodyMedium = TextStyle(
        fontFamily = RailwayFontFamily, fontWeight = FontWeight.Normal,
        fontSize = 14.sp, lineHeight = 20.sp, letterSpacing = 0.15.sp,
    ),
    bodySmall = TextStyle(
        fontFamily = RailwayFontFamily, fontWeight = FontWeight.Normal,
        fontSize = 12.sp, lineHeight = 18.sp, letterSpacing = 0.2.sp,
    ),
    labelLarge = TextStyle(
        fontFamily = RailwayFontFamily, fontWeight = FontWeight.SemiBold,
        fontSize = 14.sp, lineHeight = 20.sp, letterSpacing = 0.1.sp,
    ),
    labelMedium = TextStyle(
        fontFamily = RailwayFontFamily, fontWeight = FontWeight.Medium,
        fontSize = 12.sp, lineHeight = 16.sp, letterSpacing = 0.5.sp,
    ),
    labelSmall = TextStyle(
        fontFamily = RailwayFontFamily, fontWeight = FontWeight.Medium,
        fontSize = 11.sp, lineHeight = 16.sp, letterSpacing = 0.5.sp,
    ),
)
