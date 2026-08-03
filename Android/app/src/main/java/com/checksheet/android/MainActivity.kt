package com.checksheet.android

import android.content.Intent
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.animation.AnimatedContentTransitionScope
import androidx.compose.animation.core.tween
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.animation.slideInHorizontally
import androidx.compose.animation.slideOutHorizontally
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.SnackbarHost
import androidx.compose.material3.SnackbarHostState
import androidx.compose.material3.Surface
import androidx.compose.material3.windowsizeclass.ExperimentalMaterial3WindowSizeClassApi
import androidx.compose.material3.windowsizeclass.calculateWindowSizeClass
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.currentBackStackEntryAsState
import androidx.navigation.compose.rememberNavController
import androidx.navigation.navArgument
import com.checksheet.android.notification.SystemNotifier
import com.checksheet.android.theme.ChecksheetTheme
import com.checksheet.android.ui.components.ProvideWindowSizeClass
import com.checksheet.android.ui.approvalreview.ApprovalReviewScreen
import com.checksheet.android.ui.checksheet.ChecksheetScreen
import com.checksheet.android.ui.checksheetdetail.ChecksheetDetailScreen
import com.checksheet.android.ui.history.HistoryScreen
import com.checksheet.android.ui.home.HomeScreen
import com.checksheet.android.ui.fillchecksheet.FillChecksheetScreen
import com.checksheet.android.ui.login.LoginScreen
import com.checksheet.android.ui.notifications.NotificationEventsViewModel
import com.checksheet.android.ui.notifications.NotificationScreen
import com.checksheet.android.ui.otp.OtpScreen
import com.checksheet.android.ui.pendingapprovals.PendingApprovalsScreen
import com.checksheet.android.ui.profile.ProfileScreen
import com.checksheet.android.ui.schedule.ScheduleSelectionScreen
import com.checksheet.android.ui.session.SessionWatcherViewModel
import com.checksheet.android.ui.settings.SettingsScreen
import com.checksheet.android.ui.splash.SplashScreen
import dagger.hilt.android.AndroidEntryPoint
import java.net.URLDecoder
import java.net.URLEncoder
import java.nio.charset.StandardCharsets

@AndroidEntryPoint
class MainActivity : ComponentActivity() {

    // Set by a tapped system notification (see SystemNotifier) - read reactively from
    // ChecksheetNavHost to navigate to Notifications once the app has an authenticated screen to
    // push it on top of. androidx.compose.runtime's `by` delegate works on any Kotlin property,
    // not just inside @Composable functions, and reading it from setContent{}'s composition below
    // is what makes changes here trigger recomposition.
    private var openNotificationsRequested by mutableStateOf(false)

    @OptIn(ExperimentalMaterial3WindowSizeClassApi::class)
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        handleNotificationIntent(intent)
        setContent {
            val windowSizeClass = calculateWindowSizeClass(this)
            ChecksheetTheme {
                ProvideWindowSizeClass(windowSizeClass) {
                    Surface(modifier = Modifier.fillMaxSize(), color = MaterialTheme.colorScheme.background) {
                        ChecksheetNavHost(
                            openNotificationsRequested = openNotificationsRequested,
                            onOpenNotificationsHandled = { openNotificationsRequested = false }
                        )
                    }
                }
            }
        }
    }

    // singleTop launch mode (see AndroidManifest.xml) routes a tapped notification here instead of
    // spawning a second Activity instance, while the app is already running.
    override fun onNewIntent(intent: Intent) {
        super.onNewIntent(intent)
        setIntent(intent)
        handleNotificationIntent(intent)
    }

    private fun handleNotificationIntent(intent: Intent?) {
        if (intent?.getBooleanExtra(SystemNotifier.EXTRA_OPEN_NOTIFICATIONS, false) == true) {
            openNotificationsRequested = true
        }
    }
}

private val PRE_AUTH_ROUTE_PREFIXES = listOf("splash", "login", "otp")

// Module 31: subtle, fast (220ms) fade + short slide - a screen transition that reads as
// "responsive" rather than something the user consciously watches happen.
private const val NAV_ANIM_DURATION_MS = 220
private val NavEnterTransition: AnimatedContentTransitionScope<androidx.navigation.NavBackStackEntry>.() -> androidx.compose.animation.EnterTransition =
    { fadeIn(tween(NAV_ANIM_DURATION_MS)) + slideInHorizontally(tween(NAV_ANIM_DURATION_MS)) { fullWidth -> fullWidth / 8 } }
private val NavExitTransition: AnimatedContentTransitionScope<androidx.navigation.NavBackStackEntry>.() -> androidx.compose.animation.ExitTransition =
    { fadeOut(tween(NAV_ANIM_DURATION_MS)) }
private val NavPopEnterTransition: AnimatedContentTransitionScope<androidx.navigation.NavBackStackEntry>.() -> androidx.compose.animation.EnterTransition =
    { fadeIn(tween(NAV_ANIM_DURATION_MS)) }
private val NavPopExitTransition: AnimatedContentTransitionScope<androidx.navigation.NavBackStackEntry>.() -> androidx.compose.animation.ExitTransition =
    { fadeOut(tween(NAV_ANIM_DURATION_MS)) + slideOutHorizontally(tween(NAV_ANIM_DURATION_MS)) { fullWidth -> fullWidth / 8 } }

@Composable
fun ChecksheetNavHost(
    openNotificationsRequested: Boolean = false,
    onOpenNotificationsHandled: () -> Unit = {}
) {
    val navController = rememberNavController()
    val sessionWatcherViewModel: SessionWatcherViewModel = hiltViewModel()
    val hasValidSession by sessionWatcherViewModel.hasValidSession.collectAsStateWithLifecycle()
    val currentBackStackEntry by navController.currentBackStackEntryAsState()

    // A 401 anywhere in the app clears the stored session (see AuthInterceptor); this bounces the
    // user back to Login from wherever they are, rather than leaving them stuck on a screen that
    // can no longer load data. Pre-auth screens handle their own token checks and are excluded so
    // this never fights with Splash's own navigation or a Login/OTP attempt's own error handling.
    LaunchedEffect(hasValidSession, currentBackStackEntry) {
        val currentRoute = currentBackStackEntry?.destination?.route
        val isPreAuthRoute = currentRoute == null ||
            PRE_AUTH_ROUTE_PREFIXES.any { currentRoute.startsWith(it) }
        if (!hasValidSession && !isPreAuthRoute) {
            navController.navigate("login") {
                popUpTo("splash") { inclusive = true }
                launchSingleTop = true
            }
        }
    }

    // Tapping a system notification (Module 26) before the app has settled on an authenticated
    // screen (e.g. a cold start still sitting on Splash) must wait - navigating straight there
    // could get silently wiped out by Splash's own popUpTo("splash") once it finishes. Once the
    // user is anywhere past pre-auth, this fires and pushes Notifications on top of wherever they
    // currently are - matching what tapping a system notification is expected to do.
    LaunchedEffect(openNotificationsRequested, currentBackStackEntry) {
        val currentRoute = currentBackStackEntry?.destination?.route
        val isPreAuthRoute = currentRoute == null ||
            PRE_AUTH_ROUTE_PREFIXES.any { currentRoute.startsWith(it) }
        if (openNotificationsRequested && !isPreAuthRoute && currentRoute != "notifications") {
            navController.navigate("notifications") { launchSingleTop = true }
            onOpenNotificationsHandled()
        }
    }

    // A single app-wide SnackbarHost (rather than one per screen) so a new-notification Snackbar
    // (Module 26) can show up regardless of which screen the user is currently on - several of
    // those screens (History, Fill Checksheet, Profile, Settings) are off-limits to modify for
    // this module, so this is the only place such a cross-screen Snackbar can be wired in. No
    // topBar/bottomBar is set here, so this Scaffold only contributes the floating snackbar slot
    // and doesn't affect any individual screen's own layout underneath it.
    val notificationEventsViewModel: NotificationEventsViewModel = hiltViewModel()
    val snackbarHostState = remember { SnackbarHostState() }
    LaunchedEffect(Unit) {
        notificationEventsViewModel.newNotificationEvents.collect { notification ->
            snackbarHostState.showSnackbar(message = "${notification.title}: ${notification.message}")
        }
    }

    Scaffold(
        snackbarHost = { SnackbarHost(snackbarHostState) }
    ) { innerPadding ->
        NavHost(
            navController = navController,
            startDestination = "splash",
            modifier = Modifier.padding(innerPadding),
            enterTransition = NavEnterTransition,
            exitTransition = NavExitTransition,
            popEnterTransition = NavPopEnterTransition,
            popExitTransition = NavPopExitTransition
        ) {
            composable("splash") {
                SplashScreen(
                    onNavigateToLogin = {
                        navController.navigate("login") {
                            popUpTo("splash") { inclusive = true }
                            launchSingleTop = true
                        }
                    },
                    onNavigateToHome = {
                        navController.navigate("home") {
                            popUpTo("splash") { inclusive = true }
                            launchSingleTop = true
                        }
                    }
                )
            }
            composable("login") {
                LoginScreen(onOtpRequested = { employeeId, password ->
                    val encodedPassword = URLEncoder.encode(password, StandardCharsets.UTF_8.toString())
                    navController.navigate("otp/$employeeId/$encodedPassword")
                })
            }
            composable("otp/{employeeId}/{password}") { backStackEntry ->
                val employeeId = backStackEntry.arguments?.getString("employeeId") ?: ""
                val password = backStackEntry.arguments?.getString("password") ?: ""
                val decodedPassword = URLDecoder.decode(password, StandardCharsets.UTF_8.toString())
                OtpScreen(
                    employeeId = employeeId,
                    password = decodedPassword,
                    onVerificationSuccess = {
                        navController.navigate("home") {
                            popUpTo("login") { inclusive = false }
                            launchSingleTop = true
                        }
                    }
                )
            }
            composable("home") {
                HomeScreen(
                    onNavigateToProfile = {
                        navController.navigate("profile")
                    },
                    onNavigateToFillChecksheet = {
                        navController.navigate("fill-checksheet")
                    },
                    onNavigateToPendingApprovals = {
                        navController.navigate("pending-approvals")
                    },
                    onNavigateToFilledChecksheets = {
                        navController.navigate("history")
                    },
                    onNavigateToNotifications = {
                        navController.navigate("notifications")
                    },
                    onNavigateToSettings = {
                        navController.navigate("settings")
                    }
                )
            }
            composable("settings") {
                SettingsScreen(
                    onNavigateBack = {
                        navController.popBackStack()
                    },
                    onLogout = {
                        navController.navigate("login") {
                            popUpTo("splash") { inclusive = true }
                            launchSingleTop = true
                        }
                    }
                )
            }
            composable("profile") {
                ProfileScreen(
                    onNavigateBack = {
                        navController.popBackStack()
                    },
                    onLogout = {
                        navController.navigate("login") {
                            popUpTo("splash") { inclusive = true }
                            launchSingleTop = true
                        }
                    }
                )
            }
            composable("fill-checksheet") {
                FillChecksheetScreen(
                    onNavigateBack = {
                        navController.popBackStack()
                    },
                    onContinue = { locomotiveId, sectionId, equipmentId, templateId, workType, tractionMotorNumber, maintenanceType ->
                        val base = "checksheet/$templateId/$locomotiveId/$sectionId/$workType"
                        // Module 32: tractionMotorNumber/maintenanceType are optional query-style
                        // args (null for every equipment other than Traction Motor) rather than
                        // required path segments, since Nav Compose path segments can't be omitted.
                        // Module 36: equipmentId joins them as optional (null for an equipment-less
                        // section such as M6-HR) rather than a required path segment, for the same
                        // reason.
                        val query = listOfNotNull(
                            equipmentId?.let { "equipmentId=$it" },
                            tractionMotorNumber?.let { "tmNumber=${URLEncoder.encode(it, StandardCharsets.UTF_8.toString())}" },
                            maintenanceType?.let { "maintenanceType=${URLEncoder.encode(it, StandardCharsets.UTF_8.toString())}" }
                        ).joinToString("&")
                        navController.navigate(if (query.isEmpty()) base else "$base?$query")
                    }
                )
            }
            composable(
                route = "checksheet/{templateId}/{locomotiveId}/{sectionId}/{workType}?equipmentId={equipmentId}&tmNumber={tmNumber}&maintenanceType={maintenanceType}",
                arguments = listOf(
                    navArgument("equipmentId") { type = NavType.StringType; nullable = true; defaultValue = null },
                    navArgument("tmNumber") { type = NavType.StringType; nullable = true; defaultValue = null },
                    navArgument("maintenanceType") { type = NavType.StringType; nullable = true; defaultValue = null }
                )
            ) {
                ChecksheetScreen(
                    onNavigateBack = {
                        navController.popBackStack()
                    },
                    onSubmitSuccess = {
                        navController.popBackStack(route = "home", inclusive = false)
                    }
                )
            }
            composable("schedule-selection") {
                ScheduleSelectionScreen(
                    onNavigateBack = {
                        navController.popBackStack()
                    }
                )
            }
            composable("pending-approvals") {
                PendingApprovalsScreen(
                    onNavigateBack = {
                        navController.popBackStack()
                    },
                    onOpenChecksheet = { checksheetId ->
                        navController.navigate("approval-review/$checksheetId")
                    }
                )
            }
            composable("approval-review/{checksheetId}") {
                ApprovalReviewScreen(
                    onNavigateBack = {
                        navController.popBackStack()
                    },
                    onActionComplete = {
                        navController.popBackStack(route = "pending-approvals", inclusive = false)
                    }
                )
            }
            composable("history") {
                HistoryScreen(
                    onNavigateBack = {
                        navController.popBackStack()
                    },
                    onOpenChecksheet = { checksheetId ->
                        navController.navigate("checksheet-detail/$checksheetId")
                    }
                )
            }
            composable("checksheet-detail/{checksheetId}") {
                ChecksheetDetailScreen(
                    onNavigateBack = {
                        navController.popBackStack()
                    }
                )
            }
            composable("notifications") {
                NotificationScreen(
                    onNavigateBack = {
                        navController.popBackStack()
                    },
                    onOpenChecksheet = { checksheetId ->
                        navController.navigate("checksheet-detail/$checksheetId")
                    }
                )
            }
        }
    }
}
