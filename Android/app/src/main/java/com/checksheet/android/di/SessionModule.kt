package com.checksheet.android.di

import com.checksheet.android.data.repository.SessionRepositoryImpl
import com.checksheet.android.data.session.SessionPreferences
import com.checksheet.android.domain.repository.SessionRepository
import dagger.Binds
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
abstract class SessionModule {
    @Binds
    @Singleton
    abstract fun bindSessionRepository(
        sessionRepositoryImpl: SessionRepositoryImpl
    ): SessionRepository
}
