from sqlalchemy.orm import Session
from app.models.system_setting import SystemSetting
from app.schemas.system_setting import SystemSettingUpdate
from fastapi import HTTPException, status


def get_settings(db: Session):
    items = db.query(SystemSetting).order_by(SystemSetting.category, SystemSetting.key).all()
    return {"items": items}


def get_setting_by_key(db: Session, key: str):
    setting = db.query(SystemSetting).filter(SystemSetting.key == key).first()
    if not setting:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Setting not found")
    return setting


def update_setting(db: Session, key: str, payload: SystemSettingUpdate):
    setting = db.query(SystemSetting).filter(SystemSetting.key == key).first()
    if not setting:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Setting not found")

    setting.value = payload.value
    db.commit()
    db.refresh(setting)
    return setting
