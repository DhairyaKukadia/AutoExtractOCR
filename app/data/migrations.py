from datetime import datetime

from sqlalchemy import select

from app.data.models import AppSetting

CURRENT_SCHEMA_VERSION = '1.0.0'


def ensure_schema_version(session) -> None:
    setting = session.scalar(select(AppSetting).where(AppSetting.key == 'schema_version'))
    if setting:
        setting.value = CURRENT_SCHEMA_VERSION
        setting.updated_at = datetime.utcnow()
    else:
        session.add(AppSetting(key='schema_version', value=CURRENT_SCHEMA_VERSION))
    session.commit()
