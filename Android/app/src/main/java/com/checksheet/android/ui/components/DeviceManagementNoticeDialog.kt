package com.checksheet.android.ui.components

import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable

/**
 * Module 44: shown at most once per device, the first time the technician reaches Home after
 * logging in. This is the real, disclosed notice required alongside the System Administration
 * CLI - it is not a formality; it plainly states what the organization's IT administrators can
 * see and do on this device via that CLI, and what they explicitly cannot.
 */
@Composable
fun DeviceManagementNoticeDialog(onAcknowledge: () -> Unit) {
    AlertDialog(
        onDismissRequest = { /* Must be explicitly acknowledged - not dismissible by tapping outside. */ },
        title = { Text("Device Management Notice") },
        text = {
            Text(
                "Your organization's IT administrators can, for security purposes:\n\n" +
                    "• View this device's registration information (manufacturer, model, OS and app " +
                    "version, battery, network status, storage headroom)\n" +
                    "• View BL-DCMS's own app data footprint on this device\n" +
                    "• End active BL-DCMS login sessions on this device\n" +
                    "• Clear BL-DCMS's own application data on this device (for example, if it is " +
                    "reported lost or stolen)\n\n" +
                    "They cannot view your personal photos, messages, files, other apps, or this " +
                    "device's screen. This access is limited to BL-DCMS's own data and is performed " +
                    "only by authenticated administrators on the organization's internal network, " +
                    "with every action logged."
            )
        },
        confirmButton = {
            TextButton(onClick = onAcknowledge) {
                Text("I Understand")
            }
        }
    )
}
