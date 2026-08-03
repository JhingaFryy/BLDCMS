package com.checksheet.android.domain.repository

import com.checksheet.android.data.model.UserSummary

interface UserRepository {
    /** Technicians only - the only role that ever appears as a checksheet's technician_mobile. */
    suspend fun getTechnicians(): List<UserSummary>
}
