import json
from datetime import datetime

from app.data.models import ExtractedField, MedicalRecord
from app.data.repositories.record_repository import RecordRepository


class RecordService:
    def __init__(self, session):
        self.repo = RecordRepository(session)

    def save_record(
        self,
        *,
        form_category: str,
        source_file_name: str,
        source_file_path: str,
        raw_ocr_text: str,
        extracted_fields: dict[str, str],
        status: str,
        created_by: int,
    ) -> MedicalRecord:
        record_number = f'REC-{datetime.utcnow().strftime("%Y%m%d%H%M%S%f")}'
        record = MedicalRecord(
            record_number=record_number,
            form_category=form_category,
            patient_identifier=extracted_fields.get('patient_identifier', ''),
            patient_name=extracted_fields.get('patient_name', ''),
            form_type=extracted_fields.get('form_type', ''),
            source_file_name=source_file_name,
            source_file_path=source_file_path,
            raw_ocr_text=raw_ocr_text,
            extracted_json=json.dumps(extracted_fields),
            review_status=status,
            created_by=created_by,
        )
        fields = [
            ExtractedField(
                field_name=k,
                field_value=v,
                normalized_value=v.strip(),
                confidence_score=0.0,
                is_verified=status in {'reviewed', 'approved'},
            )
            for k, v in extracted_fields.items()
        ]
        return self.repo.create_record(record, fields)
