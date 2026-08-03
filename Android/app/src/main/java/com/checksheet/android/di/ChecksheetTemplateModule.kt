package com.checksheet.android.di

import com.checksheet.android.data.api.ChecksheetTemplateApi
import com.checksheet.android.data.repository.ChecksheetTemplateRepositoryImpl
import com.checksheet.android.domain.repository.ChecksheetTemplateRepository
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.components.SingletonComponent
import retrofit2.Retrofit
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
object ChecksheetTemplateModule {

    @Provides
    @Singleton
    fun provideChecksheetTemplateApi(retrofit: Retrofit): ChecksheetTemplateApi =
        retrofit.create(ChecksheetTemplateApi::class.java)

    @Provides
    @Singleton
    fun provideChecksheetTemplateRepository(
        checksheetTemplateApi: ChecksheetTemplateApi
    ): ChecksheetTemplateRepository =
        ChecksheetTemplateRepositoryImpl(checksheetTemplateApi)
}
