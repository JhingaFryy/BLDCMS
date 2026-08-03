package com.checksheet.android.di

import com.checksheet.android.data.api.NotificationApi
import com.checksheet.android.data.repository.NotificationRepositoryImpl
import com.checksheet.android.domain.repository.NotificationRepository
import dagger.Binds
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.components.SingletonComponent
import retrofit2.Retrofit
import javax.inject.Singleton

/** @Binds (rather than a manual @Provides factory) so NotificationRepositoryImpl's constructor
 * can gain new Hilt-resolvable dependencies (see Module 26's poll loop) without this module
 * needing to be updated every time. */
@Module
@InstallIn(SingletonComponent::class)
abstract class NotificationModule {

    @Binds
    @Singleton
    abstract fun bindNotificationRepository(
        notificationRepositoryImpl: NotificationRepositoryImpl
    ): NotificationRepository

    companion object {
        @Provides
        @Singleton
        fun provideNotificationApi(retrofit: Retrofit): NotificationApi =
            retrofit.create(NotificationApi::class.java)
    }
}
