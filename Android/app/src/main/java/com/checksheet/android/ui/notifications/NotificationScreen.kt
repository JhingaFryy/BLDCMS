package com.checksheet.android.ui.notifications

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.Cancel
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.DoneAll
import androidx.compose.material.icons.filled.Edit
import androidx.compose.material.icons.filled.HelpOutline
import androidx.compose.material.icons.filled.Info
import androidx.compose.material.icons.filled.UploadFile
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.pulltorefresh.PullToRefreshContainer
import androidx.compose.material3.pulltorefresh.rememberPullToRefreshState
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.input.nestedscroll.nestedScroll
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import com.checksheet.android.ui.components.AppCard
import com.checksheet.android.ui.components.EmptyState
import com.checksheet.android.ui.components.ErrorState
import com.checksheet.android.ui.components.ShimmerListPlaceholder
import androidx.lifecycle.compose.collectAsStateWithLifecycle

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun NotificationScreen(
    viewModel: NotificationViewModel = hiltViewModel(),
    onNavigateBack: () -> Unit = {},
    onOpenChecksheet: (Int) -> Unit = {}
) {
    val state by viewModel.uiState.collectAsStateWithLifecycle()
    val pullToRefreshState = rememberPullToRefreshState()

    // No initial refresh() call here - NotificationViewModel already loads on init{}. Triggering a
    // second one here would fire a duplicate network call every time this screen is opened.
    if (pullToRefreshState.isRefreshing) {
        LaunchedEffect(Unit) {
            viewModel.refresh()
        }
    }

    LaunchedEffect(state.loading) {
        if (!state.loading) {
            pullToRefreshState.endRefresh()
        }
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Notifications") },
                navigationIcon = {
                    IconButton(onClick = onNavigateBack) {
                        Icon(imageVector = Icons.Filled.ArrowBack, contentDescription = "Back")
                    }
                },
                actions = {
                    if (state.unreadCount > 0) {
                        IconButton(onClick = viewModel::markAllAsRead) {
                            Icon(imageVector = Icons.Filled.DoneAll, contentDescription = "Mark all as read")
                        }
                    }
                }
            )
        }
    ) { innerPadding ->
        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
                .nestedScroll(pullToRefreshState.nestedScrollConnection)
        ) {
            when {
                state.loading && state.items.isEmpty() -> {
                    ShimmerListPlaceholder(modifier = Modifier.padding(16.dp))
                }

                state.errorMessage != null && state.items.isEmpty() -> {
                    ErrorState(
                        message = state.errorMessage ?: "Unable to load notifications",
                        onRetry = viewModel::retry,
                    )
                }

                state.items.isEmpty() -> {
                    EmptyState(
                        message = "No notifications available.",
                        icon = Icons.Filled.Info,
                    )
                }

                else -> {
                    LazyColumn(
                        modifier = Modifier.fillMaxSize(),
                        contentPadding = PaddingValues(16.dp),
                        verticalArrangement = Arrangement.spacedBy(12.dp)
                    ) {
                        items(state.items, key = { it.id }) { item ->
                            NotificationRow(
                                item = item,
                                onClick = {
                                    viewModel.markAsRead(item.id)
                                    val checksheetId = item.checksheetId
                                    if (checksheetId != null) {
                                        onOpenChecksheet(checksheetId)
                                    }
                                }
                            )
                        }
                    }
                }
            }

            PullToRefreshContainer(
                state = pullToRefreshState,
                modifier = Modifier.align(Alignment.TopCenter)
            )
        }
    }
}

@Composable
private fun NotificationRow(item: NotificationItem, onClick: () -> Unit) {
    val (icon, iconColor) = notificationIconAndColor(item.type)

    AppCard(
        onClick = onClick,
        containerColor = if (item.isRead) {
            MaterialTheme.colorScheme.surface
        } else {
            MaterialTheme.colorScheme.secondaryContainer
        },
        modifier = Modifier.fillMaxWidth()
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalAlignment = Alignment.Top
        ) {
            Icon(
                imageVector = icon,
                contentDescription = null,
                tint = iconColor,
                modifier = Modifier.size(28.dp)
            )
            Spacer(modifier = Modifier.width(12.dp))
            Column(modifier = Modifier.weight(1f)) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        text = item.title,
                        style = MaterialTheme.typography.titleSmall,
                        modifier = Modifier.weight(1f)
                    )
                    if (!item.isRead) {
                        Box(
                            modifier = Modifier
                                .size(8.dp)
                                .background(color = MaterialTheme.colorScheme.primary, shape = CircleShape)
                        )
                    }
                }
                Spacer(modifier = Modifier.height(4.dp))
                Text(
                    text = notificationTypeLabel(item.type),
                    style = MaterialTheme.typography.labelSmall,
                    color = iconColor
                )
                Spacer(modifier = Modifier.height(4.dp))
                Text(
                    text = item.message,
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
                Spacer(modifier = Modifier.height(6.dp))
                Text(
                    text = item.createdAtDisplay,
                    style = MaterialTheme.typography.labelSmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
        }
    }
}

@Composable
private fun notificationIconAndColor(type: NotificationType): Pair<ImageVector, Color> = when (type) {
    NotificationType.CHECKSHEET_SUBMITTED ->
        Icons.Filled.UploadFile to MaterialTheme.colorScheme.primary

    NotificationType.CHECKSHEET_SIGNED ->
        Icons.Filled.CheckCircle to MaterialTheme.colorScheme.secondary

    NotificationType.CHECKSHEET_REJECTED ->
        Icons.Filled.Cancel to MaterialTheme.colorScheme.error

    NotificationType.CHECKSHEET_NEEDS_CORRECTION ->
        Icons.Filled.Edit to MaterialTheme.colorScheme.tertiary

    NotificationType.SYSTEM ->
        Icons.Filled.Info to MaterialTheme.colorScheme.onSurfaceVariant

    NotificationType.UNKNOWN ->
        Icons.Filled.HelpOutline to MaterialTheme.colorScheme.onSurfaceVariant
}
