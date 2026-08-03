package com.checksheet.android.data.repository

import com.checksheet.android.data.api.EquipmentApi
import com.checksheet.android.data.model.Equipment
import com.checksheet.android.domain.repository.AuthRepository
import com.checksheet.android.domain.repository.EquipmentRepository
import javax.inject.Inject

class EquipmentRepositoryImpl @Inject constructor(
    private val equipmentApi: EquipmentApi,
    private val authRepository: AuthRepository
) : EquipmentRepository {
    override suspend fun getEquipment(): List<Equipment> = equipmentApi.getEquipment()

    override suspend fun getEquipmentForCurrentUser(technology: String, locomotiveId: Int?): List<Equipment> {
        val sectionId = authRepository.getUserProfile().sectionId ?: return emptyList()

        // Module 29.12: filtering by section AND technology now happens server-side (the backend
        // joins SectionEquipmentMap and normalizes its display-style technology vocabulary against
        // this value) rather than fetching every mapping and cross-referencing it here.
        // Module 40: locomotiveId is passed straight through - the backend alone decides whether
        // it needs to further disambiguate by Locomotive Model.
        return equipmentApi.getEquipment(sectionId = sectionId, technology = technology, locomotiveId = locomotiveId)
    }
}
