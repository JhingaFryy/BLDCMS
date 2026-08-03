"""
Automatic Checksheet Validation Engine (Module 29.9).

Validates every submitted observation against its TemplateField's own metadata-declared rules
and returns a PASS/FAIL result per field. This is the single source of truth for validation -
pdf_service (and any future consumer) only ever renders whatever this module decides; nothing
here is specific to any equipment or template, and every rule is driven entirely by template
metadata (min_value/max_value, validation_rule/validation_threshold, negative_values).

Adding a new reusable rule means adding a function here and registering it in _LEAF_RULES (or,
for a cross-field rule like percentage_difference, a new validation_rule branch in
validate_checksheet_values) - never touching pdf_service.py or any Dashboard/Android code.
"""
from dataclasses import dataclass
from typing import Optional

from app.models.template_field import TemplateField

PASS_STATUS = "PASS"
FAIL_STATUS = "FAIL"


@dataclass(frozen=True)
class ValidationResult:
    status: str  # PASS_STATUS or FAIL_STATUS
    reason: Optional[str] = None


PASS = ValidationResult(PASS_STATUS)


def _parse_csv(raw: Optional[str]) -> list[str]:
    if not raw:
        return []
    return [part.strip() for part in raw.split(",") if part.strip()]


def _to_float(raw: Optional[str]) -> Optional[float]:
    if raw is None:
        return None
    try:
        return float(raw)
    except (TypeError, ValueError):
        return None


def _validate_numeric_range(field: TemplateField, value: Optional[str]) -> ValidationResult:
    """Rules 1 & 2 (Minimum Value / Range Validation): fails if the submitted observation lies
    outside [min_value, max_value]. Either bound may be absent - min_value only is a one-sided
    minimum (e.g. "Minimum 1 MOhm"), both set is a full range (e.g. Bearing Seat Dia DE/NDE).
    Driven purely by whichever field happens to have these columns set - never tied to a specific
    field_type, so any future field gains this validation just by having a min/max defined."""
    if field.min_value is None and field.max_value is None:
        return PASS

    numeric = _to_float(value)
    if numeric is None:
        return PASS  # nothing entered, or not a number - not this rule's concern

    if field.min_value is not None and numeric < field.min_value:
        return ValidationResult(FAIL_STATUS, f"{value} is below the minimum {field.min_value}")
    if field.max_value is not None and numeric > field.max_value:
        return ValidationResult(FAIL_STATUS, f"{value} is above the maximum {field.max_value}")
    return PASS


def _validate_negative_values(field: TemplateField, value: Optional[str]) -> ValidationResult:
    """Rules 5 & 6 (Green Zone / Negative Status Validation): fails if the submitted observation
    exactly matches one of this field's own template-defined negative_values (e.g. "Not in Green
    Zone", "Crack Found", "Abnormal", "Wave form Not OK", or "false" for a boolean field) - the
    list of failing values always comes from template metadata, never a hardcoded string list."""
    negative_values = _parse_csv(field.negative_values)
    if not negative_values or value is None:
        return PASS
    if value.strip() in negative_values:
        return ValidationResult(FAIL_STATUS, f"'{value}' is a defined failing condition")
    return PASS


_LEAF_RULES = [_validate_numeric_range, _validate_negative_values]


def _validate_percentage_difference(
    group: TemplateField,
    children: list[TemplateField],
    values_by_field_id: dict[int, Optional[str]],
) -> dict[int, ValidationResult]:
    """Rules 3 & 4 (Percentage Difference / Phase Imbalance Validation) - the same algorithm with
    a different, template-defined threshold: find the minimum of the group's direct children's
    submitted readings; if any pairwise absolute difference exceeds threshold% of that minimum,
    every reading in the group is marked FAIL (there is no way to isolate a single "culprit" from
    pairwise comparisons alone, so all offending values are highlighted, matching the spec)."""
    threshold = group.validation_threshold
    result = {child.id: PASS for child in children}

    if threshold is None:
        return result

    readings = [
        (child, numeric)
        for child in children
        for numeric in [_to_float(values_by_field_id.get(child.id))]
        if numeric is not None
    ]
    if len(readings) < 2:
        return result

    minimum = min(value for _, value in readings)
    if minimum == 0:
        # A zero baseline makes "% of minimum" meaningless - treat as PASS rather than raising;
        # this is a data-entry edge case, not a template design error.
        return result

    exceeded = any(
        abs(readings[i][1] - readings[j][1]) > (threshold / 100.0) * minimum
        for i in range(len(readings))
        for j in range(i + 1, len(readings))
    )
    if exceeded:
        fail = ValidationResult(FAIL_STATUS, f"Difference exceeds {threshold}% of the minimum reading")
        for child, _ in readings:
            result[child.id] = fail
    return result


def _validate_absolute_difference(
    group: TemplateField,
    children: list[TemplateField],
    values_by_field_id: dict[int, Optional[str]],
) -> dict[int, ValidationResult]:
    """Reusable validation type added for Module 32 (M35-TM Traction Motor): fails if any pairwise
    absolute difference between a group's direct children's submitted readings exceeds a flat,
    template-defined threshold - e.g. "difference between UV/VW/UW winding inductance readings
    must not exceed 0.015 mH". Distinct from percentage_difference (Rules 3/4), which scales its
    threshold by the group's minimum reading (a true percentage); here validation_threshold is
    used directly as the absolute cutoff, with no scaling - the two rules share the same
    validation_threshold column but interpret it differently, selected per-group by
    validation_rule. Same "mark every sibling FAIL together" behavior as percentage_difference,
    since pairwise comparisons alone can't isolate a single culprit reading."""
    threshold = group.validation_threshold
    result = {child.id: PASS for child in children}

    if threshold is None:
        return result

    readings = [
        (child, numeric)
        for child in children
        for numeric in [_to_float(values_by_field_id.get(child.id))]
        if numeric is not None
    ]
    if len(readings) < 2:
        return result

    exceeded = any(
        abs(readings[i][1] - readings[j][1]) > threshold
        for i in range(len(readings))
        for j in range(i + 1, len(readings))
    )
    if exceeded:
        fail = ValidationResult(FAIL_STATUS, f"Difference exceeds {threshold}")
        for child, _ in readings:
            result[child.id] = fail
    return result


_GROUP_RULES = {
    "percentage_difference": _validate_percentage_difference,
    "absolute_difference": _validate_absolute_difference,
}


def validate_checksheet_values(
    fields: list[TemplateField], values_by_field_id: dict[int, Optional[str]]
) -> dict[int, ValidationResult]:
    """Entry point: validates every submitted observation and returns a per-field-id PASS/FAIL
    result. `fields` should be every TemplateField belonging to the checksheet's template(s)
    (equipment + section common page, if any) - group fields are included so their
    validation_rule metadata can be read, but never receive a result of their own since they
    carry no observation."""
    results: dict[int, ValidationResult] = {}
    children_by_parent: dict[int, list[TemplateField]] = {}
    for field in fields:
        if field.parent_field_id is not None:
            children_by_parent.setdefault(field.parent_field_id, []).append(field)

    for field in fields:
        if field.field_type == "group":
            continue  # groups are containers - they never carry an observation of their own

        value = values_by_field_id.get(field.id)
        field_result = PASS
        for rule in _LEAF_RULES:
            outcome = rule(field, value)
            if outcome.status == FAIL_STATUS:
                field_result = outcome
                break
        results[field.id] = field_result

    # Cross-field group rules run after (and can override) individual leaf results, since they
    # depend on multiple sibling values together rather than any single field's own metadata.
    # Dispatched generically via _GROUP_RULES so a future group-level rule only ever needs a new
    # function + one entry there - never a new branch here.
    for group in fields:
        if group.field_type != "group":
            continue
        rule_fn = _GROUP_RULES.get(group.validation_rule)
        if rule_fn is None:
            continue
        children = children_by_parent.get(group.id, [])
        group_results = rule_fn(group, children, values_by_field_id)
        for field_id, outcome in group_results.items():
            if outcome.status == FAIL_STATUS:
                results[field_id] = outcome

    return results
