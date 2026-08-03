package com.checksheet.android.notification

import android.Manifest
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Build
import androidx.core.app.NotificationCompat
import androidx.core.app.NotificationManagerCompat
import androidx.core.content.ContextCompat
import com.checksheet.android.MainActivity
import com.checksheet.android.R
import com.checksheet.android.data.model.Notification
import dagger.hilt.android.qualifiers.ApplicationContext
import javax.inject.Inject
import javax.inject.Singleton

/** Posts a system notification when a new server-side notification is discovered while the app
 * is backgrounded. Only ever called from NotificationRepositoryImpl's poll loop. */
@Singleton
class SystemNotifier @Inject constructor(
    @ApplicationContext private val context: android.content.Context
) {
    companion object {
        const val CHANNEL_ID = "bl_dcms_notifications"
        const val EXTRA_OPEN_NOTIFICATIONS = "open_notifications"
        private const val CHANNEL_NAME = "Notifications"
    }

    init {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                CHANNEL_ID,
                CHANNEL_NAME,
                NotificationManager.IMPORTANCE_DEFAULT
            )
            val manager = context.getSystemService(NotificationManager::class.java)
            manager?.createNotificationChannel(channel)
        }
    }

    fun notify(notification: Notification) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU &&
            ContextCompat.checkSelfPermission(
                context,
                Manifest.permission.POST_NOTIFICATIONS
            ) != PackageManager.PERMISSION_GRANTED
        ) {
            // Never crash - a denied/not-yet-granted runtime permission just means this particular
            // notification silently doesn't show as a system notification. The in-app Snackbar path
            // (for when the app is foregrounded) is unaffected by this permission.
            return
        }

        val intent = Intent(context, MainActivity::class.java).apply {
            action = Intent.ACTION_VIEW
            flags = Intent.FLAG_ACTIVITY_NEW_TASK or
                Intent.FLAG_ACTIVITY_CLEAR_TOP or
                Intent.FLAG_ACTIVITY_SINGLE_TOP
            putExtra(EXTRA_OPEN_NOTIFICATIONS, true)
        }
        val pendingIntent = PendingIntent.getActivity(
            context,
            notification.id,
            intent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )

        val builder = NotificationCompat.Builder(context, CHANNEL_ID)
            .setSmallIcon(R.drawable.ic_notification)
            .setContentTitle(notification.title)
            .setContentText(notification.message)
            .setAutoCancel(true)
            .setContentIntent(pendingIntent)
            .setPriority(NotificationCompat.PRIORITY_DEFAULT)

        try {
            NotificationManagerCompat.from(context).notify(notification.id, builder.build())
        } catch (e: SecurityException) {
            // Defense in depth alongside the permission check above - never crash.
        }
    }
}
