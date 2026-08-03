package com.checksheet.android.di

import com.checksheet.android.data.api.SectionApi
import com.checksheet.android.data.repository.SectionRepositoryImpl
import com.checksheet.android.domain.repository.SectionRepository
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.components.SingletonComponent
import retrofit2.Retrofit
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
object SectionModule {

    @Provides
    @Singleton
    fun provideSectionApi(retrofit: Retrofit): SectionApi =
        retrofit.create(SectionApi::class.java)

    @Provides
    @Singleton
    fun provideSectionRepository(sectionApi: SectionApi): SectionRepository =
        SectionRepositoryImpl(sectionApi)
}
