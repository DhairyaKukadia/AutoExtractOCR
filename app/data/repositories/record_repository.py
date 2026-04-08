from datetime import datetime

from sqlalchemy import and_, desc, func, select

from app.data.models import ExtractedField, MedicalRecord


class RecordRepository:
    def __init__(self, session):
        self.session = session

    def create_record(self, record: MedicalRecord, fields: list[ExtractedField]) -> MedicalRecord:
        self.session.add(record)
        self.session.flush()
        for field in fields:
            field.medical_record_id = record.id
            self.session.add(field)
        self.session.commit()
        self.session.refresh(record)
        return record

    def replace_fields(self, record_id: int, extracted_fields: dict[str, str], status: str):
        self.session.query(ExtractedField).filter(ExtractedField.medical_record_id == record_id).delete()
        for key, value in extracted_fields.items():
            self.session.add(
                ExtractedField(
                    medical_record_id=record_id,
                    field_name=key,
                    field_value=value,
                    normalized_value=value.strip(),
                    confidence_score=0.0,
                    is_verified=status in {'reviewed', 'approved'},
                )
            )

    def count_records_for_year(self, year: int) -> int:
        year_start = datetime(year, 1, 1)
        year_end = datetime(year + 1, 1, 1)
        stmt = select(func.count(MedicalRecord.id)).where(and_(MedicalRecord.created_at >= year_start, MedicalRecord.created_at < year_end))
        return self.session.scalar(stmt) or 0

    def list_records(
        self,
        category: str = '',
        status: str = '',
        patient_name: str = '',
        patient_identifier: str = '',
        record_number: str = '',
        form_type: str = '',
        date_from: datetime | None = None,
        sort_by: str = "created_at",
        sort_desc: bool = True,
        limit: int = 50,
        offset: int = 0,
    ) -> list[MedicalRecord]:
        sort_map = {
            "created_at": MedicalRecord.created_at,
            "status": MedicalRecord.review_status,
            "patient": MedicalRecord.patient_name,
        }
        sort_column = sort_map.get(sort_by, MedicalRecord.created_at)
        order_column = desc(sort_column) if sort_desc else sort_column
        stmt = select(MedicalRecord).order_by(order_column)
        if category:
            stmt = stmt.where(MedicalRecord.form_category == category)
        if status:
            stmt = stmt.where(MedicalRecord.review_status == status)
        if patient_name:
            stmt = stmt.where(MedicalRecord.patient_name.ilike(f'%{patient_name}%'))
        if patient_identifier:
            stmt = stmt.where(MedicalRecord.patient_identifier.ilike(f'%{patient_identifier}%'))
        if record_number:
            stmt = stmt.where(MedicalRecord.record_number.ilike(f'%{record_number}%'))
        if form_type:
            stmt = stmt.where(MedicalRecord.form_type.ilike(f'%{form_type}%'))
        if date_from is not None:
            stmt = stmt.where(MedicalRecord.created_at >= date_from)
        stmt = stmt.limit(limit).offset(offset)
        return list(self.session.scalars(stmt))

    def count_records(
        self,
        category: str = '',
        status: str = '',
        patient_name: str = '',
        patient_identifier: str = '',
        record_number: str = '',
    ) -> int:
        stmt = select(func.count(MedicalRecord.id))
        if category:
            stmt = stmt.where(MedicalRecord.form_category == category)
        if status:
            stmt = stmt.where(MedicalRecord.review_status == status)
        if patient_name:
            stmt = stmt.where(MedicalRecord.patient_name.ilike(f'%{patient_name}%'))
        if patient_identifier:
            stmt = stmt.where(MedicalRecord.patient_identifier.ilike(f'%{patient_identifier}%'))
        if record_number:
            stmt = stmt.where(MedicalRecord.record_number.ilike(f'%{record_number}%'))
        return self.session.scalar(stmt) or 0

    def get_by_id(self, record_id: int) -> MedicalRecord | None:
        return self.session.get(MedicalRecord, record_id)
