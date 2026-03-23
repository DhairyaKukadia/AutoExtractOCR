from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.data.database import Base


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(nullable=False)
    full_name: Mapped[str] = mapped_column(nullable=False)
    role: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class FormTemplate(Base):
    __tablename__ = 'form_templates'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    template_name: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(Text, default='')
    form_category: Mapped[str] = mapped_column(nullable=False)
    version: Mapped[str] = mapped_column(default='1.0')
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class MedicalRecord(Base):
    __tablename__ = 'medical_records'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    record_number: Mapped[str] = mapped_column(unique=True, nullable=False)
    form_category: Mapped[str] = mapped_column(nullable=False)
    patient_identifier: Mapped[str] = mapped_column(default='')
    patient_name: Mapped[str] = mapped_column(default='')
    form_type: Mapped[str] = mapped_column(default='')
    template_id: Mapped[int | None] = mapped_column(ForeignKey('form_templates.id'), nullable=True)
    source_file_name: Mapped[str] = mapped_column(nullable=False)
    source_file_path: Mapped[str] = mapped_column(nullable=False)
    raw_ocr_text: Mapped[str] = mapped_column(Text, default='')
    extracted_json: Mapped[str] = mapped_column(Text, default='{}')
    review_status: Mapped[str] = mapped_column(default='draft')
    created_by: Mapped[int] = mapped_column(ForeignKey('users.id'))
    reviewed_by: Mapped[int | None] = mapped_column(ForeignKey('users.id'), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    fields: Mapped[list['ExtractedField']] = relationship(back_populates='record', cascade='all, delete-orphan')


class ExtractedField(Base):
    __tablename__ = 'extracted_fields'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    medical_record_id: Mapped[int] = mapped_column(ForeignKey('medical_records.id'))
    field_name: Mapped[str] = mapped_column(nullable=False)
    field_value: Mapped[str] = mapped_column(default='')
    normalized_value: Mapped[str] = mapped_column(default='')
    confidence_score: Mapped[float] = mapped_column(Float, default=0.0)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    notes: Mapped[str] = mapped_column(Text, default='')

    record: Mapped['MedicalRecord'] = relationship(back_populates='fields')


class AuditLog(Base):
    __tablename__ = 'audit_logs'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey('users.id'), nullable=True)
    action: Mapped[str] = mapped_column(nullable=False)
    action_details: Mapped[str] = mapped_column(Text, default='')
    entity_type: Mapped[str] = mapped_column(default='')
    entity_id: Mapped[str] = mapped_column(default='')
    status: Mapped[str] = mapped_column(default='success')
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    machine_info: Mapped[str] = mapped_column(default='')


class AppSetting(Base):
    __tablename__ = 'app_settings'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    key: Mapped[str] = mapped_column(unique=True, nullable=False)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
