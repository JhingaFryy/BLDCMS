package com.checksheet.android.ui.splash

import android.provider.Settings
import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.core.Animatable
import androidx.compose.animation.core.tween
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.alpha
import androidx.compose.ui.platform.LocalContext
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.checksheet.android.theme.Spacing
import com.checksheet.android.ui.components.cinematic.CircuitNetworkAnimation
import com.checksheet.android.ui.components.cinematic.DatabaseConnectedBanner
import com.checksheet.android.ui.components.cinematic.GlowBackground
import com.checksheet.android.ui.components.cinematic.LogoReveal
import com.checksheet.android.ui.components.cinematic.TerminalConsole
import kotlinx.coroutines.delay

/**
 * Module 47 "Cinematic Android Startup Experience": a scripted ~9s sequence (circuit network +
 * terminal console -> database-connected confirmation -> logo reveal) that plays once per launch,
 * built entirely from the `ui/components/cinematic` package - this file only ever sequences when those
 * pieces run, never touching [SplashViewModel]. The two navigation triggers below are kept in the
 * exact same condition/position they've always had; they're now additionally gated on
 * [sequenceComplete] (the cinematic sequence finishing) instead of a flat minimum-duration timer,
 * so the animation is never cut short and the app never waits longer than the sequence itself
 * plus however long the real session check takes - same "minimum display duration, driven by
 * whichever finishes last" semantics as before, just tied to real stage completion instead of a
 * guessed constant.
 */
@Composable
fun SplashScreen(
    viewModel: SplashViewModel = hiltViewModel(),
    onNavigateToLogin: () -> Unit,
    onNavigateToHome: () -> Unit
) {
    val state by viewModel.uiState.collectAsStateWithLifecycle()
    val context = LocalContext.current

    // Accessibility: if the user has disabled system animations (Settings > Accessibility >
    // Remove animations), skip the full cinematic sequence for a simple, near-instant fade -
    // rather than inventing a new in-app setting, this reads the same system preference Android
    // itself uses to decide whether to animate.
    val reduceMotion = remember {
        Settings.Global.getFloat(context.contentResolver, Settings.Global.ANIMATOR_DURATION_SCALE, 1f) == 0f
    }

    var circuitDone by remember { mutableStateOf(reduceMotion) }
    var terminalDone by remember { mutableStateOf(reduceMotion) }
    var showDatabaseBanner by remember { mutableStateOf(false) }
    var showLogo by remember { mutableStateOf(reduceMotion) }
    var sequenceComplete by remember { mutableStateOf(false) }
    val taglineAlpha = remember { Animatable(0f) }

    LaunchedEffect(circuitDone, terminalDone) {
        if (circuitDone && terminalDone && !showDatabaseBanner) {
            showDatabaseBanner = true
        }
    }

    if (reduceMotion) {
        LaunchedEffect(Unit) {
            delay(300)
            sequenceComplete = true
            taglineAlpha.animateTo(1f, tween(200))
        }
    }

    Box(modifier = Modifier.fillMaxSize()) {
        GlowBackground(modifier = Modifier.fillMaxSize())

        // Stage 1+2+3: circuit network + terminal console, together, until the logo takes over.
        AnimatedVisibility(
            visible = !showLogo,
            exit = fadeOut(tween(600)),
        ) {
            Box(modifier = Modifier.fillMaxSize()) {
                CircuitNetworkAnimation(
                    modifier = Modifier.fillMaxSize(),
                    nodeCount = 16,
                    activationIntervalMs = 140L,
                    onSettled = { circuitDone = true },
                )
                Column(
                    modifier = Modifier.fillMaxSize().padding(Spacing.lg),
                    verticalArrangement = Arrangement.Bottom,
                ) {
                    TerminalConsole(onFinished = { terminalDone = true })
                    if (showDatabaseBanner) {
                        DatabaseConnectedBanner(onFinished = { showLogo = true })
                    }
                }
            }
        }

        // Stage 5: the logo takes over as the sole focus.
        AnimatedVisibility(
            visible = showLogo,
            enter = fadeIn(tween(600)),
        ) {
            Column(
                modifier = Modifier.fillMaxSize().padding(Spacing.lg),
                verticalArrangement = Arrangement.Center,
                horizontalAlignment = Alignment.CenterHorizontally,
            ) {
                LogoReveal(
                    playShineSweep = !reduceMotion,
                    playPulse = !reduceMotion,
                    onSettled = { if (!reduceMotion) sequenceComplete = true },
                )
                Text(
                    text = "BL-DCMS · Railway Digital Checksheet Management System",
                    style = MaterialTheme.typography.labelMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    modifier = Modifier.alpha(taglineAlpha.value).padding(top = Spacing.md),
                )
            }
        }

        if (state.showRetry) {
            Column(
                modifier = Modifier.fillMaxSize().padding(Spacing.lg),
                verticalArrangement = Arrangement.Bottom,
                horizontalAlignment = Alignment.CenterHorizontally,
            ) {
                state.errorMessage?.let {
                    Text(
                        text = it,
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.error,
                        modifier = Modifier.padding(bottom = Spacing.sm),
                    )
                }
                Button(onClick = { viewModel.checkSession() }) {
                    Text("Retry")
                }
            }
        }
    }

    LaunchedEffect(showLogo) {
        if (showLogo && !reduceMotion) {
            taglineAlpha.animateTo(1f, tween(500))
        }
    }

    if (state.shouldNavigateToLogin && sequenceComplete) {
        onNavigateToLogin()
    }

    if (state.shouldNavigateToHome && sequenceComplete) {
        onNavigateToHome()
    }
}
