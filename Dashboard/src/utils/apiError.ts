/**
 * Formats an error caught from an API call into a plain, human-readable string safe to render
 * directly in JSX. FastAPI's 422 responses put a Pydantic validation error under `detail` as an
 * ARRAY of objects (`[{type, loc, msg, input, ctx, url}, ...]`), not a string - passing that
 * array straight into a React child (as `getErrorMessage()` used to, in
 * DigitalSignatureDialogV2.tsx) throws "Objects are not valid as a React child" and crashes the
 * surrounding component. This function is the one place that inspects the shape of `detail` and
 * always returns a string.
 */

interface PydanticValidationErrorItem {
  type?: string;
  loc?: Array<string | number>;
  msg?: string;
  input?: unknown;
}

// Human-readable labels for fields a supervisor might otherwise see as a raw Python/Pydantic
// identifier (e.g. "certificate_valid_to"). Deliberately only covers fields actually used in
// request bodies this app sends - falls back to a lightly cleaned-up version of the raw name for
// anything not listed here, rather than trying to anticipate every possible field.
const FIELD_LABELS: Record<string, string> = {
  certificate_subject: 'Certificate subject',
  certificate_issuer: 'Certificate issuer',
  certificate_serial_number: 'Certificate serial number',
  certificate_valid_from: 'Certificate valid-from date',
  certificate_valid_to: 'Certificate valid-to date',
  certificate_thumbprint: 'Certificate thumbprint',
  prepared_pdf_base64: 'Prepared document',
  document_digest_base64: 'Document digest',
  signed_cms_base64: 'Signed CMS payload',
  reserved_region_start: 'Signature placeholder position',
  reserved_region_end: 'Signature placeholder position',
  token_label: 'Token label',
};

function fieldLabel(loc: Array<string | number> | undefined): string {
  const fieldName = loc?.filter((part) => typeof part === 'string' && part !== 'body').pop();
  if (typeof fieldName !== 'string') return 'A field';
  return FIELD_LABELS[fieldName] ?? fieldName.replace(/_/g, ' ').replace(/^./, (c) => c.toUpperCase());
}

function describeValidationItem(item: PydanticValidationErrorItem): string {
  const label = fieldLabel(item.loc);
  switch (item.type) {
    case 'missing':
      return `${label} is missing.`;
    case 'string_type':
    case 'string_too_short':
    case 'string_too_long':
      return `${label} was not in the expected format.`;
    case 'datetime_from_date_parsing':
    case 'datetime_parsing':
      return `${label} could not be read as a valid date.`;
    case 'int_parsing':
    case 'int_type':
      return `${label} was not a valid number.`;
    default:
      // Fall back to the server's own message, but prefix with the field label so it's still
      // clear which field the problem is about, and it's always a plain string either way.
      return item.msg ? `${label}: ${item.msg}` : `${label} is invalid.`;
  }
}

function isPydanticValidationErrorArray(value: unknown): value is PydanticValidationErrorItem[] {
  return Array.isArray(value) && value.length > 0 && value.every((item) => typeof item === 'object' && item !== null);
}

export function getErrorMessage(error: unknown, fallback: string): string {
  if (typeof error === 'object' && error !== null && 'response' in error) {
    const response = (error as { response?: { data?: { detail?: unknown } } }).response;
    const detail = response?.data?.detail;
    if (isPydanticValidationErrorArray(detail)) {
      return detail.map(describeValidationItem).join(' ');
    }
    if (typeof detail === 'string' && detail) {
      return detail;
    }
    // Any other non-string, non-array detail shape (an object, a number, etc.) - still must never
    // be returned as-is, since callers render this value directly as a React child.
    if (detail !== undefined && detail !== null && typeof detail !== 'string') {
      return fallback;
    }
  }
  if (error instanceof Error && error.message) return error.message;
  return fallback;
}
