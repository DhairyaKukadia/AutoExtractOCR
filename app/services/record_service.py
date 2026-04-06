import json
from datetime import datetime
from uuid import uuid4

from app.config.constants import ReviewStatus
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
        template_id: int | None = None,
        reviewed_by: int | None = None,
    ) -> MedicalRecord:
        record_number = self._generate_record_number()
        record = MedicalRecord(
            record_number=record_number,
            form_category=form_category,
            patient_identifier=extracted_fields.get('patient_identifier', ''),
            patient_name=extracted_fields.get('patient_name', ''),
            form_type=extracted_fields.get('form_type', ''),
            template_id=template_id,
            source_file_name=source_file_name,
            source_file_path=source_file_path,
            raw_ocr_text=raw_ocr_text,
            extracted_json=json.dumps(extracted_fields),
            review_status=status,
            created_by=created_by,
            reviewed_by=reviewed_by,
        )
        fields = self._fields_from_dict(extracted_fields, status)
        return self.repo.create_record(record, fields)

    def update_record(
        self,
        *,
        record_id: int,
        extracted_fields: dict[str, str],
        raw_ocr_text: str,
        status: str,
        reviewed_by: int | None,
    ) -> MedicalRecord:
        record = self.repo.get_by_id(record_id)
        if not record:
            raise ValueError('Record not found')

        record.patient_identifier = extracted_fields.get('patient_identifier', '')
        record.patient_name = extracted_fields.get('patient_name', '')
        record.form_type = extracted_fields.get('form_type', '')
        record.raw_ocr_text = raw_ocr_text
        record.extracted_json = json.dumps(extracted_fields)
        record.review_status = status
        record.reviewed_by = reviewed_by
        record.updated_at = datetime.utcnow()

        fields = self._fields_from_dict(extracted_fields, status)
        return self.repo.update_record(record, fields)

    @staticmethod
    def _fields_from_dict(extracted_fields: dict[str, str], status: str) -> list[ExtractedField]:
        is_verified = status in {ReviewStatus.REVIEWED.value, ReviewStatus.APPROVED.value}
        return [
            ExtractedField(
                field_name=k,
                field_value=v,
                normalized_value=v.strip(),
                confidence_score=0.0,
                is_verified=is_verified,
            )
            for k, v in extracted_fields.items()
        ]

    @staticmethod
    def _generate_record_number() -> str:
        now = datetime.utcnow().strftime('%Y%m%d%H%M%S%f')
        return f'REC-{now}-{uuid4().hex[:6].upper()}'
