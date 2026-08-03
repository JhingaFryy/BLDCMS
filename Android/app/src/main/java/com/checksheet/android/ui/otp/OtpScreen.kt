package com.checksheet.android.ui.otp

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.core.LinearEasing
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.tween
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.aspectRatio
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.text.BasicTextField
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ErrorOutline
import androidx.compose.material.icons.filled.MarkEmailRead
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.SnackbarHost
import androidx.compose.material3.SnackbarHostState
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.checksheet.android.theme.RailwayTheme
import com.checksheet.android.theme.Spacing
import com.checksheet.android.ui.components.ResponsiveContainer
import com.checksheet.android.ui.components.cinematic.CircuitPatternOverlay
import com.checksheet.android.ui.components.cinematic.GlassPanel
import com.checksheet.android.ui.components.cinematic.GlowBackground
import com.checksheet.android.ui.login.GradientButton

private const val OTP_LENGTH = 6

@Composable
fun OtpScreen(
    employeeId: String,
    password: String,
    viewModel: OtpViewModel = hiltViewModel(),
    onVerificationSuccess: () -> Unit
) {
    val state by viewModel.uiState.collectAsStateWithLifecycle()
    val snackbarHostState = remember { SnackbarHostState() }

    LaunchedEffect(state.verificationSuccess) {
        if (state.verificationSuccess) {
            onVerificationSuccess()
        }
    }

    LaunchedEffect(state.resendSuccess) {
        state.resendSuccess?.let {
            snackbarHostState.showSnackbar(it)
        }
    }

    Box(modifier = Modifier.fillMaxSize()) {
        GlowBackground(modifier = Modifier.fillMaxSize())
        CircuitPatternOverlay(modifier = Modifier.fillMaxSize())

        Scaffold(
            containerColor = Color.Transparent,
            snackbarHost = { SnackbarHost(snackbarHostState) },
        ) { innerPadding ->
            ResponsiveContainer(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(innerPadding)
                    .verticalScroll(rememberScrollState())
            ) {
                Column(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(Spacing.lg),
                    verticalArrangement = Arrangement.Center,
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    Box(
                        modifier = Modifier
                            .size(72.dp)
                            .background(MaterialTheme.colorScheme.primaryContainer, CircleShape),
                        contentAlignment = Alignment.Center,
                    ) {
                        Icon(
                            imageVector = Icons.Filled.MarkEmailRead,
                            contentDescription = null,
                            tint = MaterialTheme.colorScheme.onPrimaryContainer,
                            modifier = Modifier.size(36.dp),
                        )
                    }

                    Spacer(modifier = Modifier.height(Spacing.md))

                    Text(
                        text = "Enter verification code",
                        style = MaterialTheme.typography.headlineSmall,
                        fontWeight = FontWeight.Bold,
                        textAlign = TextAlign.Center,
                    )
                    Text(
                        text = "A 6-digit OTP was sent for Employee ID $employeeId",
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                        textAlign = TextAlign.Center,
                        modifier = Modifier.padding(top = Spacing.xs, bottom = Spacing.lg)
                    )

                    GlassPanel(modifier = Modifier.fillMaxWidth()) {
                        Column(modifier = Modifier.padding(Spacing.lg)) {
                            OtpDigitBoxes(
                                value = state.otp,
                                onValueChange = viewModel::onOtpChanged,
                            )

                            GradientButton(
                                text = "Verify OTP",
                                onClick = { viewModel.verifyOtp(employeeId) },
                                enabled = !state.isLoading && state.otp.length == OTP_LENGTH,
                                loading = state.isLoading,
                                modifier = Modifier.padding(top = Spacing.md),
                            )
                        }
                    }

                    Row(
                        modifier = Modifier.padding(top = Spacing.lg),
                        verticalAlignment = Alignment.CenterVertically,
                    ) {
                        Text(
                            text = "Didn't receive the code?",
                            style = MaterialTheme.typography.bodyMedium,
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                        )
                        Spacer(modifier = Modifier.width(Spacing.xs))
                        if (state.canResend) {
                            TextButton(onClick = { viewModel.resendOtp(employeeId, password) }, enabled = !state.isLoading) {
                                Text("Resend OTP")
                            }
                        } else {
                            Text(
                                text = "Resend in ${state.countdownSeconds.toString().padStart(2, '0')}s",
                                style = MaterialTheme.typography.labelLarge,
                                color = MaterialTheme.colorScheme.primary,
                            )
                        }
                    }

                    AnimatedVisibility(visible = state.errorMessage != null, enter = fadeIn(), exit = fadeOut()) {
                        OtpErrorBanner(message = state.errorMessage ?: "")
                    }
                }
            }
        }
    }
}

/**
 * "Railway Command Center" UI overhaul: renders [value] (a single OTP string, unchanged from the
 * original single-field design) as [OTP_LENGTH] individual animated digit boxes. A single,
 * normally-invisible [BasicTextField] remains the real source of truth/focus/IME target - its
 * `value`/`onValueChange` are the exact same [value]/[onValueChange] the original bare
 * `OutlinedTextField` used, just decorated differently. This is a rendering treatment only: no
 * new state, no change to what the OTP screen actually sends to [onValueChange].
 */
@Composable
private fun OtpDigitBoxes(value: String, onValueChange: (String) -> Unit) {
    val colors = RailwayTheme.cinematicColors
    val transition = rememberInfiniteTransition(label = "otpCaret")
    val caretAlpha by transition.animateFloat(
        initialValue = 0.25f,
        targetValue = 1f,
        animationSpec = infiniteRepeatable(tween(600, easing = LinearEasing), RepeatMode.Reverse),
        label = "caretPulse",
    )

    BasicTextField(
        value = value,
        onValueChange = onValueChange,
        keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
        textStyle = TextStyle(color = Color.Transparent),
        cursorBrush = androidx.compose.ui.graphics.SolidColor(Color.Transparent),
        decorationBox = {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(Spacing.sm),
            ) {
                for (index in 0 until OTP_LENGTH) {
                    val digit = value.getOrNull(index)?.toString()
                    val isActive = index == value.length
                    Box(
                        modifier = Modifier
                            .weight(1f)
                            .aspectRatio(0.8f)
                            .clip(MaterialTheme.shapes.small)
                            .background(MaterialTheme.colorScheme.surface.copy(alpha = 0.4f))
                            .border(
                                width = if (isActive) 2.dp else 1.dp,
                                color = if (isActive) colors.wireGlow.copy(alpha = caretAlpha) else colors.trackSteelDim,
                                shape = MaterialTheme.shapes.small,
                            ),
                        contentAlignment = Alignment.Center,
                    ) {
                        Text(
                            text = digit ?: "",
                            style = MaterialTheme.typography.headlineSmall,
                            fontWeight = FontWeight.Bold,
                        )
                    }
                }
            }
        },
    )
}

@Composable
private fun OtpErrorBanner(message: String) {
    Surface(
        modifier = Modifier
            .fillMaxWidth()
            .padding(top = Spacing.md),
        shape = MaterialTheme.shapes.medium,
        color = MaterialTheme.colorScheme.errorContainer,
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(Spacing.md),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Icon(
                imageVector = Icons.Filled.ErrorOutline,
                contentDescription = null,
                tint = MaterialTheme.colorScheme.onErrorContainer,
                modifier = Modifier.size(20.dp),
            )
            Spacer(modifier = Modifier.width(Spacing.sm))
            Text(
                text = message,
                color = MaterialTheme.colorScheme.onErrorContainer,
                style = MaterialTheme.typography.bodyMedium,
            )
        }
    }
}
