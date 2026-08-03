package com.checksheet.android.di

import com.checksheet.android.data.api.ChecksheetApi
import com.checksheet.android.data.repository.ChecksheetRepositoryImpl
import com.checksheet.android.domain.repository.ChecksheetRepository
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.components.SingletonComponent
import retrofit2.Retrofit
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
object ChecksheetModule {

    @Provides
    @Singleton
    fun provideChecksheetApi(retrofit: Retrofit): ChecksheetApi =
        retrofit.create(ChecksheetApi::class.java)

    @Provides
    @Singleton
    fun provideChecksheetRepository(checksheetApi: ChecksheetApi): ChecksheetRepository =
        ChecksheetRepositoryImpl(checksheetApi)
}
