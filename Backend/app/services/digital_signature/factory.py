"""Digital Signature trust configuration.

The backend only verifies PDFs signed client-side against the trust-chain configuration below
(`dsc.trusted_ca_bundle_path`, `dsc.enable_revocation_check`), shared by
digital_signature_v2_service's verify-on-complete step and its on-demand re-verification, so both
agree on the same trust configuration. (Admin-editable from Settings > Digital Signature Trust in
the Dashboard.)
"""
from sqlalchemy.orm import Session

from app.models.system_setting import SystemSetting

TRUSTED_CA_BUNDLE_PATH_KEY = "dsc.trusted_ca_bundle_path"
ENABLE_REVOCATION_CHECK_KEY = "dsc.enable_revocation_check"


def _get_setting_value(db: Session, key: str, default: str | None) -> str | None:
    setting = db.query(SystemSetting).filter(SystemSetting.key == key).first()
    if setting is None or setting.value is None or setting.value == "":
        return default
    return setting.value


def get_trust_settings(db: Session) -> tuple[str | None, bool]:
    """(trusted_ca_bundle_path, check_revocation) - shared by digital_signature_v2_service's
    verify-on-complete step and its on-demand re-verification, so both agree on the same trust
    configuration."""
    check_revocation = str(_get_setting_value(db, ENABLE_REVOCATION_CHECK_KEY, "false")).strip().lower() in ("true", "1", "yes", "on")
    return _get_setting_value(db, TRUSTED_CA_BUNDLE_PATH_KEY, None), check_revocation
