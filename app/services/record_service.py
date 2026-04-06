import json
from datetime import datetime

from app.config.constants import FORM_CATEGORY_TO_TABLE
from app.data.models import ExtractedField, MedicalRecord
from app.data.repositories.record_repository import RecordRepository


class RecordService:
    def __init__(self, session):
        self.repo = RecordRepository(session)

    def _next_record_number(self) -> str:
        year = datetime.utcnow().year
        sequence = self.repo.count_records_for_year(year) + 1
        return f'REC-{year}-{sequence:05d}'

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
        if form_category not in FORM_CATEGORY_TO_TABLE:
            raise ValueError('Invalid form category for strict pipeline')

        if extracted_fields.get('__target_table') != FORM_CATEGORY_TO_TABLE[form_category]:
            raise ValueError('Category to database mapping is invalid')

        if not extracted_fields.get('patient_name'):
            raise ValueError('patient_name is required for structured save')

        record_number = self._next_record_number()
        patient_identifier = extracted_fields.get('mrd_no', '') or extracted_fields.get('registration_no', '') or extracted_fields.get('bbr_no', '')

        record = MedicalRecord(
            record_number=record_number,
            form_category=form_category,
            patient_identifier=patient_identifier,
            patient_name=extracted_fields.get('patient_name', ''),
            form_type=FORM_CATEGORY_TO_TABLE[form_category],
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
            if not k.startswith('__')
        ]
        return self.repo.create_record(record, fields)


    def update_record_status(self, record_id: int, new_status: str, reviewed_by: int | None = None) -> MedicalRecord:
        record = self.repo.get_by_id(record_id)
        if not record:
            raise ValueError('Record not found')
        record.review_status = new_status
        if reviewed_by is not None:
            record.reviewed_by = reviewed_by
        self.repo.session.commit()
        self.repo.session.refresh(record)
        return record
