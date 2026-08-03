"""Single enforcement point for Supervisor section-based data authorization (Module 27.5).

Every backend endpoint that returns or mutates section-scoped data (Checksheets, Equipment,
Locomotives, Templates, Reports, Dashboard statistics) must call `supervisor_section_id(current_user)`
and, when it returns a non-None value, apply `WHERE section_id = ...` (joining through
SectionEquipmentMap/ChecksheetHeader where a table has no direct section_id column). This must
never be done only in the Dashboard frontend - a Supervisor's own section is derived here from
their authenticated User row, never trusted from a client-supplied parameter.
"""

from fastapi import HTTPException, status

from app.models.user import User


def supervisor_section_id(current_user: User) -> int | None:
    """Returns the section a Supervisor is restricted to, or None for any other role (meaning:
    no section restriction applies - Admins and Technicians are unaffected by this module)."""
    if current_user.role != "Supervisor":
        return None

    if current_user.section_id is None:
        # A Supervisor with no assigned section must never fall back to seeing everything -
        # that would be the worst-case failure mode for a null/missing-data edge case.
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account has no assigned section. Contact an administrator."
        )

    return current_user.section_id
