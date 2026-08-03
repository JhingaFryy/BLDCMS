package com.checksheet.android.data.repository

import com.checksheet.android.data.api.UserApi
import com.checksheet.android.data.model.UserSummary
import com.checksheet.android.domain.repository.UserRepository
import javax.inject.Inject

class UserRepositoryImpl @Inject constructor(
    private val userApi: UserApi
) : UserRepository {
    override suspend fun getTechnicians(): List<UserSummary> =
        userApi.getUsers(skip = 0, limit = 1000, role = "Technician").items
}
