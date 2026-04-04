from datetime import datetime
from uuid import uuid4


def generate_record_uid(form_type: str) -> str:
    stamp = datetime.utcnow().strftime('%Y%m%d%H%M%S%f')
    return f'{form_type}-{stamp}-{uuid4().hex[:8]}'
