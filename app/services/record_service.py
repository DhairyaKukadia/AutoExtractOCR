import json
from datetime import datetime

from sqlalchemy.exc import IntegrityError

from app.config.constants import ALLOWED_STATUS_TRANSITIONS, FORM_CATEGORY_TO_TABLE
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
        reviewed_by: int | None = None,
    ) -> MedicalRecord:
        mapped_table = FORM_CATEGORY_TO_TABLE.get(form_category)
        if mapped_table and extracted_fields.get('__target_table') and extracted_fields.get('__target_table') != mapped_table:
            raise ValueError('Category to database mapping is invalid')

        if not extracted_fields.get('patient_name'):
            raise ValueError('patient_name is required for structured save')

        patient_identifier = (
            extracted_fields.get('patient_identifier', '')
            or extracted_fields.get('mrd_no', '')
            or extracted_fields.get('registration_no', '')
            or extracted_fields.get('bbr_no', '')
        )
        for _attempt in range(3):
            record = MedicalRecord(
                record_number=self._next_record_number(),
                form_category=form_category,
                patient_identifier=patient_identifier,
                patient_name=extracted_fields.get('patient_name', ''),
                form_type=mapped_table or extracted_fields.get('form_type', ''),
                source_file_name=source_file_name,
                source_file_path=source_file_path,
                raw_ocr_text=raw_ocr_text,
                extracted_json=json.dumps(extracted_fields),
                review_status=status,
                created_by=created_by,
                reviewed_by=reviewed_by,
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
            try:
                return self.repo.create_record(record, fields)
            except IntegrityError as exc:
                self.repo.session.rollback()
                if 'record_number' not in str(exc).lower():
                    raise

        raise ValueError('Failed to generate a unique record number after multiple attempts')

    def update_record(
        self,
        *,
        record_id: int,
        extracted_fields: dict[str, str],
        raw_ocr_text: str,
        status: str,
        reviewed_by: int | None = None,
    ) -> MedicalRecord:
        record = self.repo.get_by_id(record_id)
        if not record:
            raise ValueError('Record not found')
        allowed_next = ALLOWED_STATUS_TRANSITIONS.get(record.review_status)
        if allowed_next is not None and status != record.review_status and status not in allowed_next:
            raise ValueError(f'Invalid status transition: {record.review_status} -> {status}')

        record.raw_ocr_text = raw_ocr_text
        record.extracted_json = json.dumps(extracted_fields)
        record.review_status = status
        record.patient_name = extracted_fields.get('patient_name', record.patient_name)
        record.patient_identifier = extracted_fields.get('patient_identifier', record.patient_identifier)
        if reviewed_by is not None:
            record.reviewed_by = reviewed_by

        self.repo.replace_fields(record.id, extracted_fields, status)
        self.repo.session.commit()
        self.repo.session.refresh(record)
        return record

    def update_record_status(self, record_id: int, new_status: str, reviewed_by: int | None = None) -> MedicalRecord:
        record = self.repo.get_by_id(record_id)
        if not record:
            raise ValueError('Record not found')
        allowed_next = ALLOWED_STATUS_TRANSITIONS.get(record.review_status)
        if allowed_next is not None and new_status != record.review_status and new_status not in allowed_next:
            raise ValueError(f'Invalid status transition: {record.review_status} -> {new_status}')
        record.review_status = new_status
        if reviewed_by is not None:
            record.reviewed_by = reviewed_by
        self.repo.session.commit()
        self.repo.session.refresh(record)
        return record
