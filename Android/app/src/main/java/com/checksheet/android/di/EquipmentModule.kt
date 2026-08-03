package com.checksheet.android.di

import com.checksheet.android.data.api.EquipmentApi
import com.checksheet.android.data.api.SectionEquipmentMapApi
import com.checksheet.android.data.repository.EquipmentRepositoryImpl
import com.checksheet.android.domain.repository.AuthRepository
import com.checksheet.android.domain.repository.EquipmentRepository
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.components.SingletonComponent
import retrofit2.Retrofit
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
object EquipmentModule {

    @Provides
    @Singleton
    fun provideEquipmentApi(retrofit: Retrofit): EquipmentApi =
        retrofit.create(EquipmentApi::class.java)

    @Provides
    @Singleton
    fun provideSectionEquipmentMapApi(retrofit: Retrofit): SectionEquipmentMapApi =
        retrofit.create(SectionEquipmentMapApi::class.java)

    @Provides
    @Singleton
    fun provideEquipmentRepository(
        equipmentApi: EquipmentApi,
        authRepository: AuthRepository
    ): EquipmentRepository =
        EquipmentRepositoryImpl(equipmentApi, authRepository)
}
