package com.checksheet.android.ui.settings

enum class ThemeMode {
    SYSTEM,
    LIGHT,
    DARK
}

fun parseThemeMode(raw: String?): ThemeMode =
    when (raw) {
        "LIGHT" -> ThemeMode.LIGHT
        "DARK" -> ThemeMode.DARK
        else -> ThemeMode.SYSTEM
    }
