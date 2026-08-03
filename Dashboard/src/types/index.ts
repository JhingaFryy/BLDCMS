export type UserRole = 'Admin' | 'Supervisor' | 'Technician';

export interface UserProfile {
  id: string;
  employeeId: string;
  name: string;
  email: string;
  mobile: string;
  role: UserRole;
  status: 'Active' | 'Inactive' | 'Pending';
  section_id?: number | null;
  section_name?: string | null;
}

export interface UserListItem {
  id: number;
  employee_id: string;
  name: string;
  mobile: string;
  email?: string | null;
  role: UserRole;
  is_active: boolean;
  created_at?: string;
  section_id?: number | null;
  section_name?: string | null;
}

export interface UserListResponse {
  items: UserListItem[];
  total: number;
}

export interface UserFormValues {
  employee_id: string;
  name: string;
  mobile: string;
  email: string;
  role: UserRole;
  is_active: boolean;
  password: string;
  section_id: number | '';
}

export interface UserCreatePayload {
  employee_id: string;
  name: string;
  mobile: string;
  email?: string | null;
  role: UserRole;
  is_active: boolean;
  password: string;
  section_id?: number | null;
}

export interface UserUpdatePayload {
  name?: string;
  mobile?: string;
  email?: string | null;
  role?: UserRole;
  is_active?: boolean;
  password?: string;
  section_id?: number | null;
}

export interface LoginPayload {
  employee_id: string;
  password: string;
  rememberMe?: boolean;
}

export interface AuthResponse {
  accessToken?: string;
  access_token?: string;
  token_type?: string;
  user?: UserProfile;
}

export interface ApiErrorShape {
  detail?: string;
  message?: string;
}

export interface SectionItem {
  id?: number;
  name?: string;
  status?: string;
  created_at?: string;
  [key: string]: unknown;
}

export interface SectionFormValues {
  name: string;
}

export interface LocomotiveItem {
  id?: number;
  loco_number?: string;
  loco_model?: string;
  technology?: string;
  is_active?: boolean;
  status?: string;
  [key: string]: unknown;
}

export interface LocomotiveFormValues {
  loco_number: string;
  loco_model: string;
  is_active: boolean;
}

export interface EquipmentItem {
  id?: number;
  equipment_code?: string;
  equipment_name?: string;
  is_active?: boolean;
  used_in?: string;
  status?: string;
  section_id?: number | null;
  [key: string]: unknown;
}

export interface EquipmentFormValues {
  equipment_code: string;
  equipment_name: string;
  is_active: boolean;
}

export interface TemplateItem {
  id?: number;
  template_code?: string;
  version?: number;
  template_name?: string;
  description?: string | null;
  // Module 29.5: equipment_id is now optional - a template with equipment_id unset and
  // section_id set is a section-wide "common page" template composed ahead of every equipment
  // template in that section, rather than an equipment-specific template.
  equipment_id?: number | null;
  equipment_name?: string;
  section_id?: number | null;
  section_name?: string;
  technology?: string;
  is_active?: boolean;
  created_at?: string;
  [key: string]: unknown;
}

export interface TemplateFormValues {
  template_code: string;
  version: number;
  template_kind: 'equipment' | 'common';
  equipment_id: number | '';
  section_id: number | '';
  technology: string;
  template_name: string;
  description: string;
  is_active: boolean;
}

export interface TemplateCreatePayload {
  template_code: string;
  version: number;
  equipment_id?: number;
  section_id?: number;
  technology: string;
  template_name: string;
  description?: string | null;
}

export interface TemplateUpdatePayload {
  template_code?: string;
  version?: number;
  equipment_id?: number;
  section_id?: number;
  technology?: string;
  template_name?: string;
  description?: string | null;
  is_active?: boolean;
}

export interface TemplateFieldItem {
  id?: number;
  template_id?: number;
  template_name?: string;
  field_key?: string;
  field_label?: string;
  field_type?: string;
  display_order?: number;
  required?: boolean;
  unit?: string | null;
  default_value?: string | null;
  options?: string | null;
  help_text?: string | null;
  is_active?: boolean;
  // Archival status - set when a delete was blocked by real historical checksheet_value
  // references and the field was archived instead of removed. Archived fields are never
  // returned by the template-fields listing endpoint, so this is mostly informational.
  is_deleted?: boolean;
  deleted_at?: string | null;
  // --- Module 29.5: Dynamic Checksheet Template Engine ---
  min_value?: number | null;
  max_value?: number | null;
  decimal_precision?: number | null;
  standard_value?: string | null;
  authority_reference?: string | null;
  parent_field_id?: number | null;
  page_number?: number;
  [key: string]: unknown;
}

export interface TemplateFieldFormValues {
  template_id: number | '';
  display_order: number;
  field_label: string;
  field_key: string;
  field_type: string;
  required: boolean;
  unit: string;
  default_value: string;
  options: string;
  help_text: string;
  is_active: boolean;
  min_value: string;
  max_value: string;
  decimal_precision: string;
  standard_value: string;
  authority_reference: string;
  parent_field_id: number | '';
  page_number: number;
}

export interface TemplateFieldCreatePayload {
  template_id: number;
  field_key: string;
  field_label: string;
  field_type: string;
  display_order: number;
  required: boolean;
  unit?: string | null;
  default_value?: string | null;
  options?: string | null;
  help_text?: string | null;
  min_value?: number | null;
  max_value?: number | null;
  decimal_precision?: number | null;
  standard_value?: string | null;
  authority_reference?: string | null;
  parent_field_id?: number | null;
  page_number?: number;
}

export interface TemplateFieldDeleteResponse {
  message: string;
  archived: boolean;
}

export interface TemplateFieldUpdatePayload {
  template_id?: number;
  field_key?: string;
  field_label?: string;
  field_type?: string;
  display_order?: number;
  required?: boolean;
  unit?: string | null;
  default_value?: string | null;
  options?: string | null;
  help_text?: string | null;
  is_active?: boolean;
  min_value?: number | null;
  max_value?: number | null;
  decimal_precision?: number | null;
  standard_value?: string | null;
  authority_reference?: string | null;
  parent_field_id?: number | null;
  page_number?: number;
}

export interface MappingItem {
  id?: number;
  section_id?: number;
  section_name?: string;
  equipment_id?: number;
  equipment_name?: string;
  technology?: string;
  template_id?: number;
  template_name?: string;
  template_code?: string;
  template_version?: number;
  is_active?: boolean;
  [key: string]: unknown;
}

export interface ChecksheetValueDetailItem {
  field_id: number;
  // Breadcrumb-flattened server-side (e.g. "Bearing Seat Dia. of Rotor Shaft (for 6313) > DE") -
  // never a bare, potentially-ambiguous leaf label like "DE" alone.
  field_label: string;
  field_key: string;
  field_type: string;
  display_order: number;
  required: boolean;
  unit?: string | null;
  default_value?: string | null;
  options?: string | null;
  help_text?: string | null;
  field_value?: string | null;
  standard_value?: string | null;
  authority_reference?: string | null;
}

export interface DigitalSignatureItem {
  id: number;
  checksheet_id: number;
  supervisor_id?: number | null;
  supervisor_name: string;
  supervisor_employee_id: string;
  certificate_subject: string;
  certificate_issuer: string;
  certificate_serial_number: string;
  certificate_thumbprint: string;
  certificate_valid_from: string;
  certificate_valid_to: string;
  signing_timestamp: string;
  signature_hash: string;
  verification_status: string;
  provider: string;
  created_at: string;
}

// Module 40: shape of one certificate as listed by eMudhra emBridge's own
// POST /DSC/ListCertificate response, reached directly from the supervisor's browser at
// https://localhost.emudhra.com:26769 - never from the backend. See services/embridgeClient.ts.
// key_store_display_name is carried along so signHash() knows which token/provider to use - it's
// not part of emBridge's certificate response itself, but every certificate object handed around
// this module needs it to make a later PKCSSign call.
export interface SigningCertificateItemV2 {
  key_id: string;
  subject: string;
  issuer: string;
  serial_number: string;
  thumbprint: string;
  valid_from: string;
  valid_to: string;
  // emBridge's `certificateData` field (raw base64 DER, unconfirmed exact encoding), if present -
  // lets the backend do a precise SHA-256/DER-based certificate identity check instead of
  // falling back to a normalized serial+issuer comparison. See embridgeClient.ts.
  der_base64: string | null;
  key_store_display_name: string;
}

// Module 40: the certificate metadata the Dashboard declares to the backend BEFORE emBridge signs
// (POST .../signature-v2/prepare), and echoes back after signing so the backend can confirm the
// certificate actually embedded in the signed PDF matches what was declared (POST
// .../signature-v2/complete). Field names mirror the backend's PrepareSignatureRequestV2 schema.
export interface DeclaredCertificateV2 {
  certificate_subject: string;
  certificate_issuer: string;
  certificate_serial_number: string;
  certificate_valid_from: string;
  certificate_valid_to: string;
}

export interface ChecksheetItem {
  id?: number;
  status?: string;
  technician_mobile?: string;
  technician_name?: string;
  technician_employee_id?: string;
  locomotive_id?: number;
  section_id?: number;
  equipment_id?: number;
  template_id?: number;
  template_name?: string;
  work_type?: string;
  // Module 32: null/absent for every equipment other than Traction Motor.
  traction_motor_number?: string;
  maintenance_type?: string;
  locomotive_number?: string;
  locomotive_type?: string;
  technology?: string;
  equipment_name?: string;
  section_name?: string;
  submitted_at?: string | null;
  approved_at?: string | null;
  rejected_at?: string | null;
  rejection_reason?: string | null;
  created_at?: string;
  values?: ChecksheetValueDetailItem[];
  // Module 39: present only once this checksheet has actually been digitally signed.
  digital_signature?: DigitalSignatureItem | null;
  [key: string]: unknown;
}

export interface SystemSettingItem {
  key: string;
  value?: string | null;
  category: string;
  description?: string | null;
}

export interface ChecksheetAnalyticsFilters {
  section_id?: number;
  equipment_id?: number;
  locomotive_id?: number;
  locomotive_type?: string;
  technology?: string;
  work_type?: string;
  date_from?: string;
  date_to?: string;
  supervisor_id?: number;
}

export interface DailyTrendPoint {
  date: string;
  count: number;
}

export interface SectionCount {
  section_id: number | null;
  section_name: string | null;
  count: number;
}

export interface EquipmentCount {
  equipment_id: number | null;
  equipment_name: string | null;
  count: number;
}

export interface StatusDistribution {
  DRAFT: number;
  SUBMITTED: number;
  UNDER_REVIEW: number;
  APPROVED: number;
  REJECTED: number;
}

export interface RecentActivityItem {
  checksheet_id: number;
  event: 'SUBMITTED' | 'APPROVED' | 'REJECTED' | 'CREATED';
  at: string;
  actor_name?: string | null;
  actor_role?: string | null;
  locomotive_number?: string | null;
  equipment_name?: string | null;
  section_name?: string | null;
}

export interface ChecksheetAnalyticsSummary {
  total_locomotives: number;
  total_equipment: number;
  total_technicians: number;
  total_supervisors: number;
  today_submitted: number;
  pending_review: number;
  signed: number;
  rejected: number;
  needs_correction: number;
  daily_trend: DailyTrendPoint[];
  by_section: SectionCount[];
  by_equipment: EquipmentCount[];
  status_distribution: StatusDistribution;
  recent_activity: RecentActivityItem[];
}

export interface ServiceStatusItem {
  name: string;
  status: 'Online' | 'Offline';
  response_time_ms: number;
  last_checked: string;
  detail?: string | null;
}

export interface ServerInfo {
  cpu_usage_percent: number;
  memory_usage_percent: number;
  memory_used_gb: number;
  memory_total_gb: number;
  disk_usage_percent: number;
  disk_used_gb: number;
  disk_total_gb: number;
  uptime: string;
  python_version: string;
  fastapi_version: string;
  postgresql_version?: string | null;
  operating_system: string;
}

export interface ApplicationInfo {
  backend_version: string;
  android_version?: string | null;
  build_date?: string | null;
}

export interface DatabaseStats {
  total_users: number;
  total_technicians: number;
  total_supervisors: number;
  total_locomotives: number;
  total_equipment: number;
  total_checksheets: number;
  pending_reviews: number;
  approved: number;
  rejected: number;
}

export interface ActiveUserItem {
  employee_id: string;
  name: string;
  role: UserRole;
  login_time: string;
  last_activity: string;
}

export interface DailyCounts {
  date: string;
  signature_count: number;
  checksheet_submission_count: number;
  approval_count: number;
}

export interface SlowestEndpointItem {
  endpoint: string;
  avg_duration_ms: number;
  count: number;
}

export interface FrequentEndpointItem {
  endpoint: string;
  count: number;
}

export interface FailedRequestItem {
  timestamp: string;
  method: string;
  endpoint: string;
  status_code: number;
  duration_ms: number;
}

export interface RecentExceptionItem {
  timestamp: string;
  method: string;
  endpoint: string;
  duration_ms: number;
}

export interface RequestMetrics {
  avg_response_time_ms?: number | null;
  slowest_endpoints: SlowestEndpointItem[];
  most_frequent_endpoints: FrequentEndpointItem[];
  recent_failed_requests: FailedRequestItem[];
  recent_exceptions: RecentExceptionItem[];
}

export interface DigitalSignatureStatus {
  recent_success_count: number;
  recent_failure_count: number;
  last_signature_at?: string | null;
}

export interface PdfGenerationStats {
  average_duration_ms?: number | null;
  count_today: number;
}

export interface DatabaseConnectionInfo {
  checked_out: number;
  pool_size: number;
}

export interface SystemHealthOverview {
  service_status: ServiceStatusItem[];
  server_info: ServerInfo;
  application_info: ApplicationInfo;
  database_stats: DatabaseStats;
  active_users: ActiveUserItem[];
  daily_counts: DailyCounts;
  request_metrics: RequestMetrics;
  digital_signature_status: DigitalSignatureStatus;
  pdf_generation_stats: PdfGenerationStats;
  database_connection_info: DatabaseConnectionInfo;
}

export interface LogFileInfo {
  key: string;
  label: string;
  exists: boolean;
  size_bytes: number;
  last_modified?: string | null;
}

export interface LogTailResponse {
  key: string;
  label: string;
  lines: string[];
}

export interface SearchResultItem {
  id: number;
  label: string;
  subtitle?: string | null;
  nav_key: string;
}

export interface GlobalSearchResults {
  locomotives: SearchResultItem[];
  equipment: SearchResultItem[];
  sections: SearchResultItem[];
  users: SearchResultItem[];
  checksheets: SearchResultItem[];
  templates: SearchResultItem[];
}

export interface ActivityLogItem {
  id: number;
  action: string;
  entity_type?: string | null;
  entity_id?: number | null;
  description?: string | null;
  user_id?: number | null;
  user_name?: string | null;
  employee_id?: string | null;
  role?: string | null;
  section_id?: number | null;
  section_name?: string | null;
  old_value?: Record<string, unknown> | null;
  new_value?: Record<string, unknown> | null;
  activity_metadata?: Record<string, unknown> | null;
  created_at: string;
}

export interface PaginatedActivityLogResponse {
  items: ActivityLogItem[];
  total: number;
}

export interface OtpLogItem {
  id: number;
  user_id: number;
  employee_id?: string | null;
  user_name?: string | null;
  section_id?: number | null;
  section_name?: string | null;
  is_verified: boolean;
  attempts: number;
  // Plaintext OTP shown in lieu of a real SMS gateway - only ever present when the backend is
  // running with DEBUG=True; null in production or for any OTP generated before this existed.
  otp?: string | null;
  expires_at: string;
  created_at: string;
}

export interface PaginatedOtpLogResponse {
  items: OtpLogItem[];
  total: number;
}
