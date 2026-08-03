import api from '../api/client';
import type {
  ChecksheetAnalyticsFilters,
  ChecksheetAnalyticsSummary,
  ChecksheetItem,
  DeclaredCertificateV2,
  DigitalSignatureItem,
  EquipmentItem,
  GlobalSearchResults,
  LocomotiveItem,
  LogFileInfo,
  LogTailResponse,
  MappingItem,
  PaginatedActivityLogResponse,
  PaginatedOtpLogResponse,
  SectionItem,
  SystemHealthOverview,
  TemplateFieldCreatePayload,
  TemplateFieldDeleteResponse,
  TemplateFieldItem,
  TemplateFieldUpdatePayload,
  TemplateItem,
  TemplateCreatePayload,
  TemplateUpdatePayload,
  UserCreatePayload,
  UserListResponse,
  UserUpdatePayload,
  SystemSettingItem
} from '../types';

export const apiService = {
  getSections: () => api.get<SectionItem[]>('/sections/'),
  createSection: (payload: Partial<SectionItem>) => api.post<SectionItem>('/sections/', payload),
  updateSection: (id: number, payload: Partial<SectionItem>) => api.put<SectionItem>(`/sections/${id}`, payload),
  deleteSection: (id: number) => api.delete(`/sections/${id}`),

  getLocomotives: () => api.get<LocomotiveItem[]>('/locomotives/'),
  createLocomotive: (payload: Partial<LocomotiveItem>) => api.post<LocomotiveItem>('/locomotives/', payload),
  updateLocomotive: (id: number, payload: Partial<LocomotiveItem>) => api.put<LocomotiveItem>(`/locomotives/${id}`, payload),
  deleteLocomotive: (id: number) => api.delete(`/locomotives/${id}`),

  getEquipment: () => api.get<EquipmentItem[]>('/equipment/'),
  createEquipment: (payload: Partial<EquipmentItem>) => api.post<EquipmentItem>('/equipment/', payload),
  updateEquipment: (id: number, payload: Partial<EquipmentItem>) => api.put<EquipmentItem>(`/equipment/${id}`, payload),
  deleteEquipment: (id: number) => api.delete(`/equipment/${id}`),

  getTemplates: () => api.get<TemplateItem[]>('/templates/'),
  createTemplate: (payload: TemplateCreatePayload) => api.post<TemplateItem>('/templates/', payload),
  updateTemplate: (id: number, payload: TemplateUpdatePayload) => api.put<TemplateItem>(`/templates/${id}`, payload),
  deleteTemplate: (id: number) => api.delete(`/templates/${id}`),

  getTemplateFields: (templateId: number) => api.get<TemplateFieldItem[]>(`/template-fields/${templateId}`),
  createTemplateField: (payload: TemplateFieldCreatePayload) => api.post<TemplateFieldItem>('/template-fields/', payload),
  updateTemplateField: (id: number, payload: TemplateFieldUpdatePayload) => api.put<TemplateFieldItem>(`/template-fields/${id}`, payload),
  deleteTemplateField: (id: number) => api.delete<TemplateFieldDeleteResponse>(`/template-fields/${id}`),

  getMappings: () => api.get<MappingItem[]>('/section-equipment-map/'),
  createMapping: (payload: Partial<MappingItem>) => api.post<MappingItem>('/section-equipment-map/', payload),
  deleteMapping: (id: number) => api.delete(`/section-equipment-map/${id}`),

  getChecksheets: (params?: {
    skip?: number;
    limit?: number;
    search?: string;
    section_id?: number;
    equipment_id?: number;
    locomotive_id?: number;
    locomotive_type?: string;
    technology?: string;
    work_type?: string;
    status?: string;
    date_from?: string;
    date_to?: string;
    sort_by?: string;
    sort_order?: string;
  }) => api.get<{ items: ChecksheetItem[]; total: number }>('/checksheet/', { params }),
  createChecksheet: (payload: Partial<ChecksheetItem>) => api.post<ChecksheetItem>('/checksheet/', payload),
  updateChecksheet: (id: number, payload: Partial<ChecksheetItem>) => api.put<ChecksheetItem>(`/checksheet/${id}`, payload),
  getChecksheet: (id: number) => api.get<ChecksheetItem>(`/checksheet/${id}`),
  deleteChecksheet: (id: number) => api.delete(`/checksheet/${id}`),
  changeChecksheetStatus: (id: number, payload: { status: string; rejection_reason?: string | null }) => api.patch<ChecksheetItem>(`/checksheet/${id}/status`, payload),
  // Module 40: Digital Signature (DSC) approval workflow using eMudhra emBridge - "Approve & Sign"
  // replaces the plain PATCH .../status -> APPROVED transition, which the backend now rejects. The
  // backend hands back a raw digest (not a whole PDF) to sign - see services/embridgeClient.ts,
  // which talks to the LOCAL emBridge service directly from the browser (that's what it's for),
  // but relays the encryption round-trip through this backend - embridge.emudhra.com/helper does
  // not grant browsers of arbitrary origins CORS access, so the browser can never call it directly.
  proxyEmBridgeHelper: (payload: { requstedData: string; requestedDataType: string; requestMode: string; version: string }) =>
    api.post<{ encryptedRequest?: string | null; encryptionKeyID?: string | null; errorMsg?: string | null } & Record<string, unknown>>(
      '/checksheet/signature-v2/embridge-helper', payload,
    ),
  checkSignatureEligibilityV2: (id: number) => api.get<{ eligible: boolean }>(`/checksheet/${id}/signature-v2/eligibility`),
  prepareSignatureDocumentV2: (id: number, payload: DeclaredCertificateV2) =>
    api.post<{ prepared_pdf_base64: string; document_digest_base64: string; reserved_region_start: number; reserved_region_end: number }>(
      `/checksheet/${id}/signature-v2/prepare`, payload,
    ),
  completeSignatureV2: (id: number, payload: {
    prepared_pdf_base64: string;
    reserved_region_start: number;
    reserved_region_end: number;
    signed_cms_base64: string;
    certificate_subject: string;
    certificate_issuer: string;
    certificate_serial_number: string;
    certificate_der_base64?: string | null;
    token_label?: string | null;
  }) => api.post<ChecksheetItem>(`/checksheet/${id}/signature-v2/complete`, payload),
  getSignatureV2: (id: number) => api.get<DigitalSignatureItem>(`/checksheet/${id}/signature-v2`),
  // Module 42: fire-and-forget telemetry for client-only emBridge events (USB token
  // detected/removed, certificate selected, PIN failure) the backend has no other way to observe
  // - never awaited at the call site, never allowed to affect the signing control flow.
  reportDscClientEvent: (payload: { event_type: 'USB_TOKEN_DETECTED' | 'CERTIFICATE_SELECTED' | 'TOKEN_REMOVED' | 'PIN_FAILURE'; checksheet_id?: number | null; detail?: string | null }) =>
    api.post('/checksheet/signature-v2/client-event', payload),

  generateChecksheetPdf: (id: number) => api.post<{ message: string; pdf_path: string }>(`/checksheet/${id}/pdf/generate`),
  downloadChecksheetPdf: (id: number) => api.get(`/checksheet/${id}/pdf/download`, { responseType: 'blob' }),
  previewChecksheetPdf: (id: number) => api.get(`/checksheet/${id}/pdf/preview`, { responseType: 'blob' }),
  exportReportPdf: (params?: Record<string, unknown>) => api.get('/checksheet/report/pdf', { params, responseType: 'blob' }),
  getChecksheetAnalytics: (params?: ChecksheetAnalyticsFilters) =>
    api.get<ChecksheetAnalyticsSummary>('/checksheet/analytics/summary', { params }),

  getUsers: ({ skip, limit, search, role, is_active, section_id, sort_by, sort_order }: {
    skip: number;
    limit: number;
    search?: string;
    role?: string;
    is_active?: boolean | null;
    section_id?: number | null;
    sort_by?: string;
    sort_order?: string;
  }) => api.get<UserListResponse>('/users/', {
    params: {
      skip,
      limit,
      search: search || undefined,
      role: role || undefined,
      is_active: is_active === null || is_active === undefined ? undefined : is_active,
      section_id: section_id === null || section_id === undefined ? undefined : section_id,
      sort_by: sort_by || undefined,
      sort_order: sort_order || undefined
    }
  }),
  createUser: (payload: UserCreatePayload) => api.post('/users/', payload),
  updateUser: (id: number, payload: UserUpdatePayload) => api.put(`/users/${id}`, payload),
  deleteUser: (id: number) => api.delete(`/users/${id}`),

  getSettings: () => api.get<{ items: SystemSettingItem[] }>('/settings/'),
  updateSetting: (key: string, payload: { value: string | null }) => api.put<SystemSettingItem>(`/settings/${encodeURIComponent(key)}`, payload),

  getSystemHealthOverview: () => api.get<SystemHealthOverview>('/system-health/overview'),
  getLogFiles: () => api.get<LogFileInfo[]>('/system-health/logs'),
  getLogTail: (key: string, lines = 200) => api.get<LogTailResponse>(`/system-health/logs/${key}`, { params: { lines } }),
  downloadLogFile: (key: string) => api.get(`/system-health/logs/${key}/download`, { responseType: 'blob' }),

  globalSearch: (q: string) => api.get<GlobalSearchResults>('/search/', { params: { q } }),

  getActivities: (params?: {
    skip?: number;
    limit?: number;
    search?: string;
    date_from?: string;
    date_to?: string;
    section_id?: number;
    user_id?: number;
    role?: string;
    action?: string;
  }) => api.get<PaginatedActivityLogResponse>('/activity-logs/', { params }),
  getActivityActions: () => api.get<{ actions: string[] }>('/activity-logs/actions'),

  // Module 30: a Supervisor calling this only ever gets rows for their own section - enforced
  // server-side (app/services/otp_service.get_otp_logs), the section_id param here is purely a
  // convenience filter within whatever the backend already scoped the query down to.
  getOtpLogs: (params?: {
    skip?: number;
    limit?: number;
    section_id?: number;
    search?: string;
  }) => api.get<PaginatedOtpLogResponse>('/otp-logs/', { params })
};
