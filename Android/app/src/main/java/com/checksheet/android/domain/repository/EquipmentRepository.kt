package com.checksheet.android.domain.repository

import com.checksheet.android.data.model.Equipment

interface EquipmentRepository {
    suspend fun getEquipment(): List<Equipment>

    /** Module 29.12: equipment mapped to the current user's section AND matching [technology]
     * (Locomotive.technology's vocabulary, e.g. "3_PHASE"/"CONVENTIONAL") - filtering happens
     * server-side against SectionEquipmentMap, not client-side.
     *
     * Module 40: [locomotiveId] additionally resolves which equipment variant applies when a
     * section maps more than one equipment record to the same section+technology, distinguished
     * only by Locomotive Model (e.g. M4-HR's "Bogie Frame-1" exists separately for WAG9HC and
     * WAP-7, both 3-Phase) - the backend decides which one via the selected locomotive's
     * loco_model, never this app. Optional: omitting it (or passing null) keeps the exact
     * pre-Module-40 behavior for every other section. */
    suspend fun getEquipmentForCurrentUser(technology: String, locomotiveId: Int? = null): List<Equipment>
}
