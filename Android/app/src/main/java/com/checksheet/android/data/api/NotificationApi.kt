package com.checksheet.android.data.api

import com.checksheet.android.data.model.MarkAllReadResponse
import com.checksheet.android.data.model.Notification
import com.checksheet.android.data.model.PaginatedNotificationResponse
import com.checksheet.android.data.model.UnreadCountResponse
import retrofit2.http.GET
import retrofit2.http.PATCH
import retrofit2.http.Path
import retrofit2.http.Query

interface NotificationApi {
    @GET("/notifications/")
    suspend fun getNotifications(
        @Query("skip") skip: Int,
        @Query("limit") limit: Int
    ): PaginatedNotificationResponse

    @PATCH("/notifications/{notificationId}/read")
    suspend fun markAsRead(@Path("notificationId") notificationId: Int): Notification

    @PATCH("/notifications/read-all")
    suspend fun markAllAsRead(): MarkAllReadResponse

    /** Lightweight poll target - a single count, no row payload. */
    @GET("/notifications/unread-count")
    suspend fun getUnreadCount(): UnreadCountResponse

    /** Incremental sync target - only notifications created after [after], so the poller never
     * re-downloads the full history on each tick. */
    @GET("/notifications/since")
    suspend fun getNotificationsSince(
        @Query("after") after: String,
        @Query("limit") limit: Int = 50
    ): List<Notification>
}
