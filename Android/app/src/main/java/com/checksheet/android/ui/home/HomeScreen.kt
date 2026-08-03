package com.checksheet.android.ui.home

import android.Manifest
import android.content.pm.PackageManager
import android.os.Build
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.core.tween
import androidx.compose.animation.fadeIn
import androidx.compose.animation.slideInVertically
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.lazy.grid.itemsIndexed
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import kotlinx.coroutines.delay
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Assignment
import androidx.compose.material.icons.filled.AssignmentTurnedIn
import androidx.compose.material.icons.filled.History
import androidx.compose.material.icons.filled.Notifications
import androidx.compose.material.icons.filled.Person
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material3.Badge
import androidx.compose.material3.BadgedBox
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.TopAppBarDefaults
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import androidx.core.content.ContextCompat
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.checksheet.android.theme.RailwayTheme
import com.checksheet.android.theme.Spacing
import com.checksheet.android.ui.components.DeviceManagementNoticeDialog
import com.checksheet.android.ui.components.ErrorState
import com.checksheet.android.ui.components.ModuleCard
import com.checksheet.android.ui.components.ShimmerCard
import com.checksheet.android.ui.components.WelcomeCard
import com.checksheet.android.ui.components.cinematic.CircuitPatternOverlay
import com.checksheet.android.ui.components.cinematic.GlowBackground

private data class DashboardItem(
    val title: String,
    val description: String,
    val icon: ImageVector,
    val onClick: () -> Unit
)

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun HomeScreen(
    viewModel: HomeViewModel = hiltViewModel(),
    onNavigateToFillChecksheet: () -> Unit = {},
    onNavigateToFilledChecksheets: () -> Unit = {},
    onNavigateToProfile: () -> Unit = {},
    onNavigateToSettings: () -> Unit = {},
    onNavigateToPendingApprovals: () -> Unit = {},
    onNavigateToNotifications: () -> Unit = {}
) {
    val state by viewModel.uiState.collectAsStateWithLifecycle()

    // System notifications (Module 26) require this runtime permission on API 33+ - Home is the
    // first authenticated screen the user reaches, so it's requested once here. A denial just
    // means system notifications silently don't show; the in-app Snackbar path is unaffected.
    val context = LocalContext.current
    val notificationPermissionLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.RequestPermission()
    ) { }
    LaunchedEffect(Unit) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU &&
            ContextCompat.checkSelfPermission(
                context,
                Manifest.permission.POST_NOTIFICATIONS
            ) != PackageManager.PERMISSION_GRANTED
        ) {
            notificationPermissionLauncher.launch(Manifest.permission.POST_NOTIFICATIONS)
        }
    }

    val dashboardItems = buildList {
        add(
            DashboardItem(
                title = "Fill Checksheet",
                description = "Create a new checksheet.",
                icon = Icons.Filled.Assignment,
                onClick = onNavigateToFillChecksheet
            )
        )
        add(
            DashboardItem(
                title = "Filled Checksheets",
                description = "View submitted checksheets.",
                icon = Icons.Filled.History,
                onClick = onNavigateToFilledChecksheets
            )
        )
        add(
            DashboardItem(
                title = "Profile",
                description = "View profile information.",
                icon = Icons.Filled.Person,
                onClick = onNavigateToProfile
            )
        )
        add(
            DashboardItem(
                title = "Settings",
                description = "Application settings.",
                icon = Icons.Filled.Settings,
                onClick = onNavigateToSettings
            )
        )
        if (state.user?.role == "Supervisor" || state.user?.role == "Admin") {
            add(
                DashboardItem(
                    title = "Pending Approvals",
                    description = "Review submitted checksheets.",
                    icon = Icons.Filled.AssignmentTurnedIn,
                    onClick = onNavigateToPendingApprovals
                )
            )
        }
    }

    Box(modifier = Modifier.fillMaxSize()) {
        GlowBackground(modifier = Modifier.fillMaxSize())
        CircuitPatternOverlay(modifier = Modifier.fillMaxSize())

        Scaffold(
            containerColor = Color.Transparent,
            topBar = {
                TopAppBar(
                    colors = TopAppBarDefaults.topAppBarColors(containerColor = Color.Transparent),
                    title = {
                        Column {
                            Text(
                                text = "BL-DCMS",
                                style = MaterialTheme.typography.titleLarge,
                                color = RailwayTheme.cinematicColors.wireGlow,
                            )
                            Text(
                                text = "Railway Digital Checksheet Management System",
                                style = MaterialTheme.typography.labelSmall
                            )
                        }
                    },
                    actions = {
                        IconButton(onClick = onNavigateToNotifications) {
                            BadgedBox(
                                badge = {
                                    if (state.unreadNotificationCount > 0) {
                                        Badge {
                                            Text(state.unreadNotificationCount.toString())
                                        }
                                    }
                                }
                            ) {
                                Icon(
                                    imageVector = Icons.Filled.Notifications,
                                    contentDescription = "Notifications"
                                )
                            }
                        }
                    }
                )
            }
        ) { innerPadding ->
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(innerPadding)
                    .padding(Spacing.md)
            ) {
                when {
                    state.loading -> ShimmerCard(modifier = Modifier.fillMaxWidth())
                    state.errorMessage != null -> ErrorState(
                        message = state.errorMessage ?: "Unable to load your profile",
                        onRetry = viewModel::retry,
                        modifier = Modifier.fillMaxWidth().height(160.dp),
                    )
                    state.user != null -> WelcomeCard(
                        name = state.user!!.name,
                        employeeId = state.user!!.employeeId,
                        section = state.user!!.sectionName ?: "-",
                        role = state.user!!.role,
                    )
                }

                Spacer(modifier = Modifier.height(Spacing.md))

                LazyVerticalGrid(
                    columns = GridCells.Adaptive(minSize = 160.dp),
                    horizontalArrangement = Arrangement.spacedBy(Spacing.md),
                    verticalArrangement = Arrangement.spacedBy(Spacing.md),
                    modifier = Modifier
                        .fillMaxWidth()
                        .weight(1f)
                ) {
                    itemsIndexed(dashboardItems, key = { _, item -> item.title }) { index, item ->
                        var visible by remember { mutableStateOf(false) }
                        LaunchedEffect(Unit) {
                            delay(60L * index)
                            visible = true
                        }
                        AnimatedVisibility(
                            visible = visible,
                            enter = fadeIn(tween(300)) + slideInVertically(tween(300)) { it / 4 },
                        ) {
                            ModuleCard(
                                title = item.title,
                                description = item.description,
                                icon = item.icon,
                                onClick = item.onClick,
                            )
                        }
                    }
                }
            }
        }
    }

    if (state.showDeviceManagementNotice) {
        DeviceManagementNoticeDialog(onAcknowledge = viewModel::acknowledgeDeviceManagementNotice)
    }
}
