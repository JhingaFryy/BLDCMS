from sqlalchemy.orm import Session
from sqlalchemy import or_, desc, asc
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.security.password import hash_password
from app.models.section import Section

def get_users(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    search: str = None,
    role: str = None,
    is_active: bool = None,
    section_id: int = None,
    sort_by: str = None,
    sort_order: str = "asc"
):
    query = db.query(User)

    # Filtering by Search
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            or_(
                User.employee_id.ilike(search_filter),
                User.name.ilike(search_filter),
                User.mobile.ilike(search_filter),
                User.email.ilike(search_filter)
            )
        )

    # Filtering by Role
    if role:
        query = query.filter(User.role == role)

    # Filtering by Status (is_active)
    if is_active is not None:
        query = query.filter(User.is_active == is_active)

    # Filtering by Section
    if section_id is not None:
        query = query.filter(User.section_id == section_id)

    # Total count after filters, before pagination
    total = query.count()

    # Sorting
    if sort_by:
        col = getattr(User, sort_by, None)
        if col:
            if sort_order.lower() == "desc":
                query = query.order_by(desc(col))
            else:
                query = query.order_by(asc(col))
    else:
        # Default sort by created_at desc
        query = query.order_by(desc(User.created_at))

    # Pagination
    items = query.offset(skip).limit(limit).all()

    return {
        "items": items,
        "total": total
    }

def create_user(db: Session, user_data: UserCreate):
    # Check duplicate employee_id
    existing_employee = db.query(User).filter(User.employee_id == user_data.employee_id).first()
    if existing_employee:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Employee ID already exists"
        )

    # Check duplicate mobile
    existing_mobile = db.query(User).filter(User.mobile == user_data.mobile).first()
    if existing_mobile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mobile number already exists"
        )

    # Validate section assignment rules
    section_id = getattr(user_data, 'section_id', None)
    if user_data.role and (user_data.role.value if hasattr(user_data.role, 'value') else user_data.role) in ['Supervisor', 'Technician'] and not section_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Section is required for Supervisor and Technician roles")

    if section_id is not None:
        section = db.query(Section).filter(Section.id == section_id).first()
        if not section:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Section not found")

    new_user = User(
        employee_id=user_data.employee_id,
        name=user_data.name,
        mobile=user_data.mobile,
        email=user_data.email,
        password_hash=hash_password(user_data.password),
        role=user_data.role.value if hasattr(user_data.role, 'value') else user_data.role,
        is_active=user_data.is_active,
        section_id=section_id
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def update_user(db: Session, user_id: int, user_data: UserUpdate):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if user_data.mobile is not None:
        existing_mobile = db.query(User).filter(User.mobile == user_data.mobile, User.id != user_id).first()
        if existing_mobile:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mobile number already exists"
            )
        user.mobile = user_data.mobile

    if user_data.name is not None:
        user.name = user_data.name

    if user_data.email is not None:
        user.email = user_data.email

    if user_data.role is not None:
        user.role = user_data.role.value if hasattr(user_data.role, 'value') else user_data.role

    # Section assignment handling. model_fields_set (not hasattr, which is always True on a
    # Pydantic model regardless of whether the field was actually sent) is what distinguishes
    # "the request didn't mention section_id at all - leave it alone" from "the request
    # explicitly sent section_id: null - clear it". Getting this wrong previously meant any
    # partial PUT that simply omitted section_id (e.g. just renaming a user) silently wiped their
    # section assignment.
    if "section_id" in user_data.model_fields_set:
        if user_data.section_id is not None:
            section = db.query(Section).filter(Section.id == user_data.section_id).first()
            if not section:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Section not found")
            user.section_id = user_data.section_id
        else:
            # explicit null allows removing section (e.g., promoting to Admin)
            user.section_id = None

    # Validated AFTER both role and section_id above have been applied, so a single request that
    # promotes a user to Supervisor/Technician AND assigns their section in the same call is
    # correctly accepted, not rejected against the pre-update section_id.
    if user.role in ['Supervisor', 'Technician'] and not user.section_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Section is required for Supervisor and Technician roles")

    if user_data.is_active is not None:
        user.is_active = user_data.is_active

    if user_data.password is not None and user_data.password != "":
        user.password_hash = hash_password(user_data.password)

    db.commit()
    db.refresh(user)
    return user

def delete_user(db: Session, user_id: int, current_user_id: int):
    if user_id == current_user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete the currently logged-in administrator"
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    db.delete(user)
    try:
        db.commit()
    except IntegrityError:
        # Nearly every real user has at least one referencing row (a login session, a checksheet
        # they touched, an OTP log, an activity log entry) that these foreign keys deliberately do
        # NOT cascade-delete, to keep historical/audit records intact - so a hard delete on any
        # user with real activity was always going to fail here. Surface that clearly instead of
        # letting the IntegrityError propagate as an unhandled 500.
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete this user: they have existing activity history (sessions, "
                   "checksheets, logs, etc.) that must be preserved. Deactivate the user instead.",
        )
    return {"message": "User deleted successfully"}
