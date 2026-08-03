package com.checksheet.android.di

import com.checksheet.android.data.api.LocomotiveApi
import com.checksheet.android.data.repository.LocomotiveRepositoryImpl
import com.checksheet.android.domain.repository.LocomotiveRepository
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.components.SingletonComponent
import retrofit2.Retrofit
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
object LocomotiveModule {

    @Provides
    @Singleton
    fun provideLocomotiveApi(retrofit: Retrofit): LocomotiveApi =
        retrofit.create(LocomotiveApi::class.java)

    @Provides
    @Singleton
    fun provideLocomotiveRepository(locomotiveApi: LocomotiveApi): LocomotiveRepository =
        LocomotiveRepositoryImpl(locomotiveApi)
}
