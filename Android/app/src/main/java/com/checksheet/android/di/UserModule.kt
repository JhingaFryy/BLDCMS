package com.checksheet.android.di

import com.checksheet.android.data.api.UserApi
import com.checksheet.android.data.repository.UserRepositoryImpl
import com.checksheet.android.domain.repository.UserRepository
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.components.SingletonComponent
import retrofit2.Retrofit
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
object UserModule {

    @Provides
    @Singleton
    fun provideUserApi(retrofit: Retrofit): UserApi =
        retrofit.create(UserApi::class.java)

    @Provides
    @Singleton
    fun provideUserRepository(userApi: UserApi): UserRepository =
        UserRepositoryImpl(userApi)
}
