package com.checksheet.android.renderer

/**
 * Internal, renderer-facing field type vocabulary.
 *
 * The backend's TemplateFieldType enum (app/schemas/template_field.py) sends: text, textarea,
 * number, numeric_range, group, select, radio, checkbox, date, datetime, boolean.
 *
 * [fromBackendValue] normalizes those raw strings onto this richer vocabulary:
 * - select / radio -> DROPDOWN (both are "choose one of [options]"; no distinct radio component exists)
 * - textarea -> MULTILINE_TEXT
 * - datetime -> DATE (rendered with the same date component; no separate combined date+time UI)
 * - numeric_range -> NUMERIC_RANGE (Module 29.5: min/max-validated numeric input with a confirm-out-of-range dialog)
 * - group -> GROUP (Module 29.5: a container of other fields, rendered recursively - see GroupComponent)
 *
 * TIME and READ_ONLY are not reachable from today's backend data - they are forward-compatible
 * slots, exactly like the explicitly-planned future types (IMAGE, SIGNATURE, GPS, BARCODE, QR_CODE,
 * FILE_UPLOAD) that also don't exist in the backend yet. Any raw value that doesn't match a known
 * mapping resolves to UNKNOWN, which always renders safely (via UnsupportedFieldComponent) instead of
 * crashing.
 */
enum class FieldType {
    TEXT,
    NUMBER,
    NUMERIC_RANGE,
    GROUP,
    BOOLEAN,
    CHECKBOX,
    DROPDOWN,
    MULTILINE_TEXT,
    DATE,
    TIME,
    READ_ONLY,
    UNKNOWN;

    companion object {
        fun fromBackendValue(rawType: String): FieldType = when (rawType.trim().lowercase()) {
            "text" -> TEXT
            "number" -> NUMBER
            "numeric_range" -> NUMERIC_RANGE
            "group" -> GROUP
            "boolean" -> BOOLEAN
            "checkbox" -> CHECKBOX
            "select", "radio" -> DROPDOWN
            "textarea" -> MULTILINE_TEXT
            "date", "datetime" -> DATE
            else -> UNKNOWN
        }
    }
}
