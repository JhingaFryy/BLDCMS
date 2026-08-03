package com.checksheet.android.util

import android.content.Context
import com.checksheet.android.data.session.SessionPreferences
import com.checksheet.android.data.session.SettingsPreferences
import java.io.File
import javax.inject.Inject

/**
 * Module 44: executes a CLI-issued "CLEAR_APP_DATA" command (see /auth/me's
 * pending_admin_command field). Deliberately touches ONLY directories the Android OS itself
 * sandboxes to this app - [Context.cacheDir], [Context.filesDir], and
 * [Context.getExternalFilesDir] are all app-private by OS design and are physically
 * inaccessible to any other app without root, so this cannot reach another app's data or the
 * user's personal files (photos, downloads, messages, etc.) even in principle - the scope
 * ("application data only") is enforced by the platform, not just by this code's intent.
 *
 * This is a disclosed capability: the technician is informed during the one-time device-
 * management notice (see ui/common/DeviceManagementNoticeDialog.kt) that IT may clear the app's
 * own data for security reasons (e.g. a lost/stolen device) - this is not hidden or covert.
 */
class DeviceDataClearer @Inject constructor(
    private val sessionPreferences: SessionPreferences,
    private val settingsPreferences: SettingsPreferences,
) {
    /** Wipes the session, app preferences, cached checksheet PDFs and any other app-private
     * files/cache - leaving the app in the same state as a fresh install, minus needing to
     * actually reinstall it. Always ends with no valid session, so the caller can rely on the
     * technician being routed back to Login immediately afterwards. */
    suspend fun clearAll(context: Context) {
        sessionPreferences.clearSession()
        runCatching { settingsPreferences.clearAll() }

        deleteContents(context.cacheDir)
        deleteContents(context.filesDir)
        context.getExternalFilesDir(null)?.let { deleteContents(it) }
    }

    private fun deleteContents(directory: File) {
        val children = directory.listFiles() ?: return
        for (child in children) {
            runCatching {
                if (child.isDirectory) {
                    child.deleteRecursively()
                } else {
                    child.delete()
                }
            }
        }
    }
}
