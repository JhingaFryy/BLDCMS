from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database.base import Base


class TemplateField(Base):
    __tablename__ = "template_fields"

    id = Column(Integer, primary_key=True, index=True)

    template_id = Column(
        Integer,
        ForeignKey("checksheet_templates.id"),
        nullable=False
    )

    field_key = Column(String(100), nullable=False)

    field_label = Column(String(255), nullable=False)

    field_type = Column(String(30), nullable=False)

    display_order = Column(Integer, nullable=False)

    required = Column(Boolean, default=True)

    unit = Column(String(30))

    default_value = Column(Text)

    options = Column(Text)

    help_text = Column(Text)

    is_active = Column(Boolean, default=True)

    # Soft-delete/archival: set together when a DELETE is blocked by real historical
    # checksheet_value references (FK: checksheet_value.field_id) instead of raising a
    # ForeignKeyViolation - see template_field_service.delete_field. Distinct from is_active,
    # which an admin may also toggle manually without the field ever having been "deleted".
    is_deleted = Column(Boolean, nullable=False, default=False)
    deleted_at = Column(DateTime, nullable=True)

    # --- Module 29.5: Dynamic Checksheet Template Engine ---
    # All generic/reusable - never named after any specific equipment (e.g. TMB), so the same
    # columns serve every future equipment's template.

    # Numeric range validation (field_type == 'numeric_range'). Unit reuses the existing `unit`
    # column above rather than duplicating it.
    min_value = Column(Float, nullable=True)
    max_value = Column(Float, nullable=True)
    decimal_precision = Column(Integer, nullable=True)

    # Read-only reference columns shown alongside the editable observation in a checklist-style
    # row ("Sr No" and "Checking Point Details" are already covered by the existing
    # display_order/field_label columns - only "Standard" and "Authority" are genuinely new).
    standard_value = Column(Text, nullable=True)
    authority_reference = Column(String(255), nullable=True)

    # Self-referential grouping (field_type == 'group') - supports arbitrary nesting depth, so
    # "Run Test After Assembly" -> "No Load Current" -> "U"/"V"/"W" is just three levels of the
    # same parent_field_id chain, with every label/unit/range still coming from this same table.
    parent_field_id = Column(Integer, ForeignKey("template_fields.id"), nullable=True)

    # Multi-page templates. Defaults to 1 so every pre-existing field (created before this
    # module) is implicitly "page 1" with no data migration required.
    page_number = Column(Integer, nullable=False, default=1, server_default="1")

    # --- Module 29.9: Automatic Checksheet Validation Engine ---
    # See app/services/validation_service.py for how these are consumed. Rules 1/2 (minimum/range)
    # need no column of their own - they're already fully expressed by min_value/max_value above.

    # Opt-in identifier for a cross-field rule that can't be inferred from a single field's own
    # metadata alone - currently only 'percentage_difference' (Rules 3/4), set on a GROUP field.
    validation_rule = Column(String(50), nullable=True)

    # Generic percentage parameter for validation_rule='percentage_difference' (10% for winding
    # resistance/inductance comparison, 5% for phase/lug temperature imbalance) - reusable for any
    # future percentage-based rule, not specific to this one.
    validation_threshold = Column(Float, nullable=True)

    # Comma-separated list of this field's own option/boolean values that constitute a FAIL
    # (Rules 5/6), e.g. "Not in Green Zone", "Crack Found", "Abnormal", "false" - always read from
    # here, never hardcoded in the validation engine or the PDF generator.
    negative_values = Column(Text, nullable=True)

    template = relationship(
        "ChecksheetTemplate",
        back_populates="fields"
    )

    parent = relationship("TemplateField", remote_side=[id], backref="children")

    def breadcrumb_label(self) -> str:
        """Flattens a possibly-nested (GROUP) field into one readable label - e.g. a "DE" leaf
        under "Bearing Seat Dia. of Rotor Shaft (for 6313)" becomes "Bearing Seat Dia. of Rotor
        Shaft (for 6313) > DE", since a bare "DE"/"U"/"V" alone is ambiguous once several groups
        reuse the same leaf labels. Shared by pdf_service and checksheet_service so every consumer
        (PDF, Dashboard, Android) shows the same qualified label without duplicating this logic."""
        parts = [self.field_label]
        parent = self.parent
        while parent is not None:
            parts.append(parent.field_label)
            parent = parent.parent
        return " > ".join(reversed(parts))

    def effective_standard_value(self) -> str | None:
        """A grouped leaf (e.g. "Winding Resistance for Comparison > RY") usually has no
        standard_value of its own - the original paper checksheet lists Standard/Authority once
        per checking point (the group, e.g. "Difference not more than 10%"), not once per
        sub-observation. Walks up the parent chain and returns the nearest ancestor's value,
        falling back to this field's own value first. Shared by pdf_service and checksheet_service
        so every consumer (PDF, Dashboard, Android) resolves the same inherited value."""
        field = self
        while field is not None:
            if field.standard_value:
                return field.standard_value
            field = field.parent
        return None

    def effective_authority_reference(self) -> str | None:
        """Same inheritance as effective_standard_value(), for authority_reference - the two are
        resolved independently since a group may set one but not the other (e.g. a sub-group only
        adds its own standard_value while the authority still comes from a higher ancestor)."""
        field = self
        while field is not None:
            if field.authority_reference:
                return field.authority_reference
            field = field.parent
        return None
