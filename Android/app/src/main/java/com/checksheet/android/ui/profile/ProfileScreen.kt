package com.checksheet.android.ui.profile

import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.Badge
import androidx.compose.material.icons.filled.Email
import androidx.compose.material.icons.filled.Groups
import androidx.compose.material.icons.filled.Logout
import androidx.compose.material.icons.filled.Person
import androidx.compose.material.icons.filled.Phone
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.FilledTonalButton
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.checksheet.android.data.model.UserProfileResponse
import com.checksheet.android.theme.Spacing
import com.checksheet.android.ui.components.AppCard
import com.checksheet.android.ui.components.AvatarPlaceholder
import com.checksheet.android.ui.components.ErrorState
import com.checksheet.android.ui.components.RoleBadge
import com.checksheet.android.ui.components.ShimmerCard

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ProfileScreen(
    viewModel: ProfileViewModel = hiltViewModel(),
    onNavigateBack: () -> Unit = {},
    onLogout: () -> Unit = {}
) {
    val state by viewModel.uiState.collectAsStateWithLifecycle()
    val currentUser = state.user
    var showLogoutDialog by remember { mutableStateOf(false) }

    LaunchedEffect(state.loggedOut) {
        if (state.loggedOut) {
            onLogout()
        }
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Profile") },
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
        bottomBar = {
            Surface(shadowElevation = 4.dp) {
                FilledTonalButton(
                    onClick = { showLogoutDialog = true },
                    enabled = !state.isLoggingOut,
                    shape = MaterialTheme.shapes.medium,
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(Spacing.md)
                        .height(52.dp)
                ) {
                    if (state.isLoggingOut) {
                        CircularProgressIndicator(modifier = Modifier.size(20.dp), strokeWidth = 2.dp)
                    } else {
                        Icon(imageVector = Icons.Filled.Logout, contentDescription = null, modifier = Modifier.size(20.dp))
                        Spacer(modifier = Modifier.width(Spacing.sm))
                        Text("Logout", style = MaterialTheme.typography.titleMedium)
                    }
                }
            }
        }
    ) { innerPadding ->
        when {
            state.loading -> {
                Column(modifier = Modifier.fillMaxSize().padding(innerPadding).padding(Spacing.md)) {
                    repeat(4) { ShimmerCard(modifier = Modifier.padding(bottom = Spacing.sm)) }
                }
            }

            state.errorMessage != null -> {
                ErrorState(
                    message = state.errorMessage ?: "Unable to load profile",
                    onRetry = viewModel::retry,
                    modifier = Modifier.fillMaxSize().padding(innerPadding),
                )
            }

            currentUser != null -> {
                ProfileContent(user = currentUser, modifier = Modifier.padding(innerPadding))
            }
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
private fun ProfileContent(user: UserProfileResponse, modifier: Modifier = Modifier) {
    Column(
        modifier = modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(Spacing.lg),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        AvatarPlaceholder(name = user.name, size = 96.dp)

        Spacer(modifier = Modifier.height(Spacing.md))

        Text(text = user.name, style = MaterialTheme.typography.headlineSmall)
        Spacer(modifier = Modifier.height(Spacing.xs))
        RoleBadge(role = user.role)

        Spacer(modifier = Modifier.height(Spacing.lg))

        ProfileFieldCard(label = "Employee Name", value = user.name, icon = Icons.Filled.Person)
        ProfileFieldCard(label = "Employee ID", value = user.employeeId, icon = Icons.Filled.Badge)
        ProfileFieldCard(label = "Section", value = user.sectionName ?: "-", icon = Icons.Filled.Groups)
        ProfileFieldCard(label = "Email", value = user.email ?: "-", icon = Icons.Filled.Email)
        ProfileFieldCard(label = "Mobile Number", value = user.mobile ?: "-", icon = Icons.Filled.Phone)
    }
}

@Composable
private fun ProfileFieldCard(label: String, value: String, icon: ImageVector) {
    AppCard(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 6.dp)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(Spacing.md),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Icon(
                imageVector = icon,
                contentDescription = null,
                tint = MaterialTheme.colorScheme.primary,
                modifier = Modifier.size(22.dp),
            )
            Spacer(modifier = Modifier.width(Spacing.md))
            Column {
                Text(
                    text = label,
                    style = MaterialTheme.typography.labelMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
                Text(
                    text = value,
                    style = MaterialTheme.typography.bodyLarge
                )
            }
        }
    }
}
