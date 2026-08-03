from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.system_setting import (
    SystemSettingsResponse,
    SystemSettingResponse,
    SystemSettingUpdate
)
from app.security.dependencies import require_admin
from app.services.activity_log_service import Action, log_activity
from app.services.system_setting_service import (
    get_settings,
    get_setting_by_key,
    update_setting
)

router = APIRouter(
    prefix="/settings",
    tags=["Settings"]
)

@router.get("/", response_model=SystemSettingsResponse)
def list_settings(
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    return get_settings(db)

@router.get("/{key}", response_model=SystemSettingResponse)
def get_setting(
    key: str,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    return get_setting_by_key(db, key)

@router.put("/{key}", response_model=SystemSettingResponse)
def update_setting_endpoint(
    key: str,
    payload: SystemSettingUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    before = get_setting_by_key(db, key)
    old_value = before.value if before else None

    updated_setting = update_setting(db, key, payload)
    log_activity(
        db,
        Action.SYSTEM_SETTING_CHANGED,
        user=current_user,
        entity_type="system_setting",
        description=f"{current_user.employee_id} changed setting {key}",
        old_value={"value": old_value},
        new_value={"value": updated_setting.value},
    )
    return updated_setting
