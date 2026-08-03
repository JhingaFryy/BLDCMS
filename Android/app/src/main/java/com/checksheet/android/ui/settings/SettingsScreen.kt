package com.checksheet.android.ui.settings

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ColumnScope
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.Groups
import androidx.compose.material.icons.filled.Info
import androidx.compose.material.icons.filled.Logout
import androidx.compose.material.icons.filled.Person
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material.icons.filled.Wifi
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Divider
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.FilledTonalButton
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.RadioButton
import androidx.compose.material3.Scaffold
import androidx.compose.material3.SnackbarHost
import androidx.compose.material3.SnackbarHostState
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.checksheet.android.BuildConfig
import com.checksheet.android.theme.RailwayTheme
import com.checksheet.android.theme.Spacing
import com.checksheet.android.ui.components.AppCard
import com.checksheet.android.ui.components.ErrorState
import kotlinx.coroutines.launch
import java.util.Calendar

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SettingsScreen(
    viewModel: SettingsViewModel = hiltViewModel(),
    onNavigateBack: () -> Unit = {},
    onLogout: () -> Unit = {}
) {
    val state by viewModel.uiState.collectAsStateWithLifecycle()
    var showLogoutDialog by remember { mutableStateOf(false) }
    val snackbarHostState = remember { SnackbarHostState() }
    val coroutineScope = rememberCoroutineScope()

    LaunchedEffect(state.loggedOut) {
        if (state.loggedOut) {
            onLogout()
        }
    }

    LaunchedEffect(state.snackbarMessage) {
        val message = state.snackbarMessage
        if (message != null) {
            coroutineScope.launch {
                snackbarHostState.showSnackbar(message)
                viewModel.onSnackbarShown()
            }
        }
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Settings") },
                navigationIcon = {
                    IconButton(onClick = onNavigateBack) {
                        Icon(
                            imageVector = Icons.Filled.ArrowBack,
                            contentDescription = "Back"
                        )
                    }
                }
            )
        },
        snackbarHost = { SnackbarHost(snackbarHostState) }
    ) { innerPadding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
                .verticalScroll(rememberScrollState())
                .padding(Spacing.md),
            verticalArrangement = Arrangement.spacedBy(Spacing.md)
        ) {
            GeneralSection(
                themeMode = state.themeMode,
                onThemeModeChange = viewModel::setThemeMode
            )

            AccountSection(
                state = state,
                onLogoutClick = { showLogoutDialog = true },
                onRetry = viewModel::retry
            )

            ApplicationSection(
                connectionStatus = state.connectionStatus,
                onTestConnection = viewModel::testConnection
            )

            AboutSection(backendVersion = state.backendVersion)

            AuthoritiesSection()

            Spacer(modifier = Modifier.height(Spacing.xs))
        }
    }

    if (showLogoutDialog) {
        AlertDialog(
            onDismissRequest = { showLogoutDialog = false },
            title = { Text("Logout") },
            text = { Text("Are you sure you want to logout?") },
            confirmButton = {
                TextButton(onClick = {
                    showLogoutDialog = false
                    viewModel.logout()
                }) {
                    Text("Logout")
                }
            },
            dismissButton = {
                TextButton(onClick = { showLogoutDialog = false }) {
                    Text("Cancel")
                }
            }
        )
    }
}

@Composable
private fun SectionCard(
    title: String,
    icon: ImageVector,
    content: @Composable ColumnScope.() -> Unit
) {
    AppCard(modifier = Modifier.fillMaxWidth()) {
        Column(modifier = Modifier.padding(Spacing.md)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Box(
                    modifier = Modifier
                        .size(36.dp)
                        .clip(CircleShape)
                        .background(MaterialTheme.colorScheme.primaryContainer),
                    contentAlignment = Alignment.Center,
                ) {
                    Icon(
                        imageVector = icon,
                        contentDescription = null,
                        tint = MaterialTheme.colorScheme.onPrimaryContainer,
                        modifier = Modifier.size(20.dp),
                    )
                }
                Spacer(modifier = Modifier.width(Spacing.sm))
                Text(text = title, style = MaterialTheme.typography.titleMedium)
            }
            Spacer(modifier = Modifier.height(Spacing.sm))
            Divider()
            Spacer(modifier = Modifier.height(Spacing.sm))
            content()
        }
    }
}

@Composable
private fun GeneralSection(
    themeMode: ThemeMode,
    onThemeModeChange: (ThemeMode) -> Unit
) {
    SectionCard(title = "General", icon = Icons.Filled.Settings) {
        Text(
            text = "Theme",
            style = MaterialTheme.typography.labelMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
        Spacer(modifier = Modifier.height(Spacing.sm))

        ThemeOptionRow(
            label = "System Default",
            selected = themeMode == ThemeMode.SYSTEM,
            onClick = { onThemeModeChange(ThemeMode.SYSTEM) }
        )
        ThemeOptionRow(
            label = "Light",
            selected = themeMode == ThemeMode.LIGHT,
            onClick = { onThemeModeChange(ThemeMode.LIGHT) }
        )
        ThemeOptionRow(
            label = "Dark",
            selected = themeMode == ThemeMode.DARK,
            onClick = { onThemeModeChange(ThemeMode.DARK) }
        )
    }
}

@Composable
private fun ThemeOptionRow(label: String, selected: Boolean, onClick: () -> Unit) {
    Surface(
        modifier = Modifier
            .fillMaxWidth()
            .clip(MaterialTheme.shapes.small)
            .clickable(onClick = onClick),
        shape = MaterialTheme.shapes.small,
        color = if (selected) MaterialTheme.colorScheme.primaryContainer.copy(alpha = 0.4f) else androidx.compose.ui.graphics.Color.Transparent,
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = Spacing.xs, vertical = Spacing.xs),
            verticalAlignment = Alignment.CenterVertically
        ) {
            RadioButton(selected = selected, onClick = onClick)
            Spacer(modifier = Modifier.width(Spacing.xs))
            Text(text = label, style = MaterialTheme.typography.bodyLarge)
        }
    }
}

@Composable
private fun AccountSection(
    state: SettingsUiState,
    onLogoutClick: () -> Unit,
    onRetry: () -> Unit
) {
    SectionCard(title = "Account", icon = Icons.Filled.Person) {
        when {
            state.loading -> {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.Center
                ) {
                    CircularProgressIndicator(modifier = Modifier.size(32.dp))
                }
            }

            state.errorMessage != null -> {
                ErrorState(
                    message = state.errorMessage,
                    onRetry = onRetry,
                    modifier = Modifier.fillMaxWidth().height(180.dp),
                )
            }

            state.user != null -> {
                AccountFieldRow(label = "Employee Name", value = state.user.name)
                AccountFieldRow(label = "Employee ID", value = state.user.employeeId)
                AccountFieldRow(label = "Role", value = state.user.role ?: "-")
                AccountFieldRow(label = "Section", value = state.user.sectionName ?: "-")
            }
        }

        Spacer(modifier = Modifier.height(Spacing.md))

        FilledTonalButton(
            onClick = onLogoutClick,
            enabled = !state.isLoggingOut,
            shape = MaterialTheme.shapes.medium,
            modifier = Modifier.fillMaxWidth().height(48.dp)
        ) {
            if (!state.isLoggingOut) {
                Icon(imageVector = Icons.Filled.Logout, contentDescription = null, modifier = Modifier.size(18.dp))
                Spacer(modifier = Modifier.width(Spacing.xs))
            }
            Text(if (state.isLoggingOut) "Logging out..." else "Logout")
        }
    }
}

@Composable
private fun AccountFieldRow(label: String, value: String) {
    Column(modifier = Modifier.padding(vertical = 6.dp)) {
        Text(
            text = label,
            style = MaterialTheme.typography.labelMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
        Spacer(modifier = Modifier.height(2.dp))
        Text(text = value, style = MaterialTheme.typography.bodyLarge)
    }
}

@Composable
private fun ApplicationSection(
    connectionStatus: ConnectionStatus,
    onTestConnection: () -> Unit
) {
    SectionCard(title = "Application", icon = Icons.Filled.Wifi) {
        AccountFieldRow(label = "Backend Server URL", value = BuildConfig.API_BASE_URL)

        Spacer(modifier = Modifier.height(Spacing.sm))

        val extended = RailwayTheme.extendedColors
        val (indicatorColor, statusLabel) = when (connectionStatus) {
            ConnectionStatus.CONNECTED -> extended.success to "Connected"
            ConnectionStatus.DISCONNECTED -> MaterialTheme.colorScheme.error to "Disconnected"
            ConnectionStatus.CHECKING -> MaterialTheme.colorScheme.onSurfaceVariant to "Checking..."
            ConnectionStatus.UNKNOWN -> MaterialTheme.colorScheme.onSurfaceVariant to "Unknown"
        }

        Row(verticalAlignment = Alignment.CenterVertically) {
            Box(
                modifier = Modifier
                    .size(12.dp)
                    .clip(CircleShape)
                    .background(color = indicatorColor)
            )
            Spacer(modifier = Modifier.width(Spacing.sm))
            Text(text = statusLabel, style = MaterialTheme.typography.bodyMedium)
        }

        Spacer(modifier = Modifier.height(Spacing.sm))

        OutlinedButton(
            onClick = onTestConnection,
            enabled = connectionStatus != ConnectionStatus.CHECKING,
            shape = MaterialTheme.shapes.medium,
            modifier = Modifier.fillMaxWidth()
        ) {
            Text(if (connectionStatus == ConnectionStatus.CHECKING) "Testing..." else "Test Connection")
        }
    }
}

@Composable
private fun AboutSection(backendVersion: String?) {
    SectionCard(title = "About", icon = Icons.Filled.Info) {
        AccountFieldRow(label = "App Name", value = "BL-DCMS")
        AccountFieldRow(label = "Version", value = BuildConfig.VERSION_NAME)
        AccountFieldRow(label = "Version Code", value = BuildConfig.VERSION_CODE.toString())
        AccountFieldRow(label = "Backend Version", value = backendVersion ?: "Not available")
        AccountFieldRow(label = "Organization", value = "Indian Railways")

        val year = Calendar.getInstance().get(Calendar.YEAR)
        Spacer(modifier = Modifier.height(Spacing.xs))
        Text(
            text = "© $year Indian Railways. All rights reserved.",
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
    }
}

@Composable
private fun AuthoritiesSection() {
    SectionCard(title = "Authorities", icon = Icons.Filled.Groups) {
        Text(
            text = "Approving Authorities",
            style = MaterialTheme.typography.labelMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
        AccountFieldRow(label = "Sr. Divisional Electrical Engineer/TRS/BL", value = "Mr. R. C. Meena")
        AccountFieldRow(label = "Divisional Electrical Engineer", value = "Mr. Suresh Kumar")

        Spacer(modifier = Modifier.height(Spacing.sm))
        Divider()
        Spacer(modifier = Modifier.height(Spacing.sm))

        Text(
            text = "Developed By",
            style = MaterialTheme.typography.labelMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
        AccountFieldRow(label = "Tech-III", value = "Mr. Jatin Pardeshi")
        AccountFieldRow(label = "Tech-II", value = "Mr. Neelkumar Patel")
    }
}
