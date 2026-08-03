package com.checksheet.android.ui.login

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.foundation.background
import androidx.compose.foundation.interaction.MutableInteractionSource
import androidx.compose.foundation.interaction.collectIsPressedAsState
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.offset
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.animation.core.Animatable
import androidx.compose.animation.core.EaseOutCubic
import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.tween
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Badge
import androidx.compose.material.icons.filled.ErrorOutline
import androidx.compose.material.icons.filled.Lock
import androidx.compose.material.icons.filled.Visibility
import androidx.compose.material.icons.filled.VisibilityOff
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.alpha
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.text.input.VisualTransformation
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.checksheet.android.ui.components.ResponsiveContainer
import com.checksheet.android.ui.components.cinematic.CircuitPatternOverlay
import com.checksheet.android.ui.components.cinematic.GlassPanel
import com.checksheet.android.ui.components.cinematic.GlowBackground
import com.checksheet.android.ui.components.cinematic.LogoReveal
import com.checksheet.android.ui.components.cinematic.railwayTextFieldColors
import com.checksheet.android.theme.RailwayTheme
import com.checksheet.android.theme.Spacing
import kotlinx.coroutines.delay

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun LoginScreen(
    viewModel: LoginViewModel = hiltViewModel(),
    onOtpRequested: (String, String) -> Unit
) {
    val state by viewModel.uiState.collectAsStateWithLifecycle()
    var passwordVisible by rememberSaveable { mutableStateOf(false) }

    // Module 47, Stage 6: the login card doesn't just appear - it slides up and fades in slightly
    // after the logo (rendered by LoginBrandHeader below) has already settled, and the fields/
    // button fade in last. Purely presentational, local to this screen; every ViewModel binding
    // below is unaffected.
    val cardOffset = remember { Animatable(48f) }
    val cardAlpha = remember { Animatable(0f) }
    val contentAlpha = remember { Animatable(0f) }

    LaunchedEffect(Unit) {
        delay(250)
        cardAlpha.animateTo(1f, tween(450))
        cardOffset.animateTo(0f, tween(550, easing = EaseOutCubic))
        delay(100)
        contentAlpha.animateTo(1f, tween(400))
    }

    Box(modifier = Modifier.fillMaxSize()) {
        GlowBackground(modifier = Modifier.fillMaxSize())
        CircuitPatternOverlay(modifier = Modifier.fillMaxSize())

        Scaffold(containerColor = androidx.compose.ui.graphics.Color.Transparent) { innerPadding ->
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
                    LoginBrandHeader()

                    Spacer(modifier = Modifier.height(Spacing.xl))

                    GlassPanel(
                        modifier = Modifier
                            .fillMaxWidth()
                            .offset(y = cardOffset.value.dp)
                            .alpha(cardAlpha.value)
                    ) {
                        Column(modifier = Modifier.padding(Spacing.lg).alpha(contentAlpha.value)) {
                            OutlinedTextField(
                                value = state.employeeId,
                                onValueChange = viewModel::onEmployeeIdChanged,
                                label = { Text("Employee ID") },
                                leadingIcon = { Icon(Icons.Filled.Badge, contentDescription = null) },
                                singleLine = true,
                                shape = MaterialTheme.shapes.small,
                                colors = railwayTextFieldColors(),
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .padding(bottom = Spacing.md)
                            )

                            OutlinedTextField(
                                value = state.password,
                                onValueChange = viewModel::onPasswordChanged,
                                label = { Text("Password") },
                                leadingIcon = { Icon(Icons.Filled.Lock, contentDescription = null) },
                                singleLine = true,
                                shape = MaterialTheme.shapes.small,
                                colors = railwayTextFieldColors(),
                                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Password),
                                visualTransformation = if (passwordVisible) VisualTransformation.None else PasswordVisualTransformation(),
                                trailingIcon = {
                                    IconButton(onClick = { passwordVisible = !passwordVisible }) {
                                        Icon(
                                            imageVector = if (passwordVisible) Icons.Filled.VisibilityOff else Icons.Filled.Visibility,
                                            contentDescription = if (passwordVisible) "Hide password" else "Show password"
                                        )
                                    }
                                },
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .padding(bottom = Spacing.lg)
                            )

                            GradientButton(
                                text = "Request OTP",
                                onClick = { viewModel.requestOtp() },
                                enabled = !state.isLoading,
                                loading = state.isLoading,
                                modifier = Modifier.graphicsLayer {
                                    val entranceScale = 0.95f + 0.05f * contentAlpha.value
                                    scaleX = entranceScale
                                    scaleY = entranceScale
                                },
                            )
                        }
                    }

                    AnimatedVisibility(visible = state.errorMessage != null, enter = fadeIn(), exit = fadeOut()) {
                        LoginErrorBanner(message = state.errorMessage ?: "")
                    }
                }
            }
        }
    }

    val requestedEmployeeId = state.requestedEmployeeId
    if (state.otpRequested && requestedEmployeeId != null) {
        onOtpRequested(requestedEmployeeId, state.password)
    }
}

/**
 * "Railway Command Center" UI overhaul: shared gradient-filled, press-morphing primary action
 * button used on Login/OTP - purely presentational (still just a `Button` with an `onClick`), so
 * every caller keeps whatever ViewModel function it already wires to [onClick] unchanged.
 */
@Composable
fun GradientButton(text: String, onClick: () -> Unit, enabled: Boolean, loading: Boolean, modifier: Modifier = Modifier) {
    val colors = RailwayTheme.cinematicColors
    val interactionSource = remember { MutableInteractionSource() }
    val isPressed by interactionSource.collectIsPressedAsState()
    val scale by animateFloatAsState(if (isPressed) 0.97f else 1f, tween(120), label = "buttonPressScale")

    Button(
        onClick = onClick,
        enabled = enabled,
        interactionSource = interactionSource,
        shape = MaterialTheme.shapes.medium,
        contentPadding = ButtonDefaults.ContentPadding,
        colors = ButtonDefaults.buttonColors(containerColor = androidx.compose.ui.graphics.Color.Transparent, disabledContainerColor = androidx.compose.ui.graphics.Color.Transparent),
        modifier = modifier
            .fillMaxWidth()
            .height(52.dp)
            .graphicsLayer { scaleX = scale; scaleY = scale }
            .background(
                brush = Brush.horizontalGradient(listOf(MaterialTheme.colorScheme.primary, colors.wireGlow)),
                shape = MaterialTheme.shapes.medium,
            ),
    ) {
        if (loading) {
            CircularProgressIndicator(
                strokeWidth = 2.dp,
                modifier = Modifier.size(22.dp),
                color = MaterialTheme.colorScheme.onPrimary,
            )
        } else {
            Text(text, style = MaterialTheme.typography.titleMedium)
        }
    }
}

@Composable
private fun LoginBrandHeader() {
    // Module 47: the official logo, settled in place (no shine sweep/pulse loop here - that's
    // Splash's one-time reveal; here it's just a static, already-arrived brand mark).
    LogoReveal(
        logoSize = 92.dp,
        playShineSweep = false,
        playPulse = false,
    )
    Spacer(modifier = Modifier.height(Spacing.sm))
    Text(
        text = "BL-DCMS",
        style = MaterialTheme.typography.headlineMedium,
        fontWeight = FontWeight.Bold,
        textAlign = TextAlign.Center,
    )
    Text(
        text = "Railway Digital Checksheet Management System",
        style = MaterialTheme.typography.bodyMedium,
        color = MaterialTheme.colorScheme.onSurfaceVariant,
        textAlign = TextAlign.Center,
        modifier = Modifier.padding(top = Spacing.xs)
    )
}

@Composable
private fun LoginErrorBanner(message: String) {
    Surface(
        modifier = Modifier
            .fillMaxWidth()
            .padding(top = Spacing.md),
        shape = MaterialTheme.shapes.medium,
        color = MaterialTheme.colorScheme.errorContainer,
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(Spacing.md)
        ) {
            Row(verticalAlignment = Alignment.CenterVertically) {
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
}
