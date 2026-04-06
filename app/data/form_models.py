from __future__ import annotations

from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.data.database import Base


class MasterForm(Base):
    __tablename__ = 'master_forms'
    __table_args__ = (
        CheckConstraint("form_type IN ('pathology_hematology','clinical_chemistry','blood_request')", name='ck_master_forms_form_type'),
        CheckConstraint("urgency_type IN ('urgent','routine') OR urgency_type IS NULL", name='ck_master_forms_urgency_type'),
        CheckConstraint(
            "review_status IN ('pending','reviewed','approved','rejected')",
            name='ck_master_forms_review_status',
        ),
        Index('idx_master_forms_form_type', 'form_type'),
        Index('idx_master_forms_patient_name', 'patient_name'),
        Index('idx_master_forms_registration_no', 'registration_no'),
        Index('idx_master_forms_mrd_no', 'mrd_no'),
        Index('idx_master_forms_doctor_name', 'doctor_name'),
        Index('idx_master_forms_upload_datetime', 'upload_datetime'),
        Index('idx_master_forms_lab_accession_no', 'laboratory_accession_no'),
        Index('idx_master_forms_bbr_no', 'bbr_no'),
    )

    master_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    record_uid: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    form_type: Mapped[str] = mapped_column(String(64), nullable=False)
    source_file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    upload_datetime: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    patient_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    age: Mapped[str | None] = mapped_column(String(64), nullable=True)
    sex: Mapped[str | None] = mapped_column(String(32), nullable=True)
    age_sex_text: Mapped[str | None] = mapped_column(String(128), nullable=True)

    registration_no: Mapped[str | None] = mapped_column(String(128), nullable=True)
    mrd_no: Mapped[str | None] = mapped_column(String(128), nullable=True)

    hospital_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    ward_unit_opd: Mapped[str | None] = mapped_column(String(255), nullable=True)
    doctor_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    doctor_contact_no: Mapped[str | None] = mapped_column(String(64), nullable=True)

    sample_or_specimen_type: Mapped[str | None] = mapped_column(String(128), nullable=True)
    collection_date: Mapped[str | None] = mapped_column(String(32), nullable=True)
    collection_time: Mapped[str | None] = mapped_column(String(32), nullable=True)
    collection_am_pm: Mapped[str | None] = mapped_column(String(8), nullable=True)

    clinical_note_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    diagnosis: Mapped[str | None] = mapped_column(Text, nullable=True)
    remarks: Mapped[str | None] = mapped_column(Text, nullable=True)

    urgency_type: Mapped[str | None] = mapped_column(String(16), nullable=True)

    lab_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    laboratory_accession_no: Mapped[str | None] = mapped_column(String(128), nullable=True)
    bbr_no: Mapped[str | None] = mapped_column(String(128), nullable=True)

    raw_ocr_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    ocr_confidence: Mapped[float | None] = mapped_column(nullable=True)
    review_status: Mapped[str] = mapped_column(String(16), nullable=False, default='pending')

    pathology_hematology_form: Mapped['PathologyHematologyForm | None'] = relationship(
        back_populates='master_form', cascade='all, delete-orphan', uselist=False
    )
    clinical_chemistry_form: Mapped['ClinicalChemistryForm | None'] = relationship(
        back_populates='master_form', cascade='all, delete-orphan', uselist=False
    )
    blood_request_form: Mapped['BloodRequestForm | None'] = relationship(
        back_populates='master_form', cascade='all, delete-orphan', uselist=False
    )


class PathologyHematologyForm(Base):
    __tablename__ = 'pathology_hematology_form'
    __table_args__ = (
        CheckConstraint("recent_blood_transfusion_flag IN ('yes','no') OR recent_blood_transfusion_flag IS NULL"),
        CheckConstraint("hemoglobinopathy_family_history_flag IN ('yes','no') OR hemoglobinopathy_family_history_flag IS NULL"),
        CheckConstraint('sender_signature_present IN (0,1)'),
        CheckConstraint('quality_ok IN (0,1)'),
        CheckConstraint('hemolysed IN (0,1)'),
        CheckConstraint('quantity_not_sufficient IN (0,1)'),
        CheckConstraint('delayed_transport IN (0,1)'),
        CheckConstraint('improper_transport IN (0,1)'),
        CheckConstraint('improper_container IN (0,1)'),
        CheckConstraint('incomplete_details_in_form IN (0,1)'),
        CheckConstraint('accepted IN (0,1)'),
        CheckConstraint('accepted_with_remark IN (0,1)'),
        CheckConstraint('rejected IN (0,1)'),
        CheckConstraint('receiver_signature_present IN (0,1)'),
    )

    pathology_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    master_id: Mapped[int] = mapped_column(ForeignKey('master_forms.master_id', ondelete='CASCADE'), nullable=False, unique=True)

    recent_blood_transfusion_flag: Mapped[str | None] = mapped_column(String(8), nullable=True)
    recent_blood_transfusion_details: Mapped[str | None] = mapped_column(Text, nullable=True)

    hemoglobinopathy_family_history_flag: Mapped[str | None] = mapped_column(String(8), nullable=True)
    hemoglobinopathy_family_history_details: Mapped[str | None] = mapped_column(Text, nullable=True)

    sample_type_other_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    body_fluid_source: Mapped[str | None] = mapped_column(Text, nullable=True)
    critical_report_phone: Mapped[str | None] = mapped_column(String(64), nullable=True)

    sender_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    sender_role: Mapped[str | None] = mapped_column(String(128), nullable=True)
    sender_signature_present: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    lab_receipt_time: Mapped[str | None] = mapped_column(String(32), nullable=True)
    lab_receipt_am_pm: Mapped[str | None] = mapped_column(String(8), nullable=True)
    lab_date: Mapped[str | None] = mapped_column(String(32), nullable=True)

    quality_ok: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    hemolysed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    quantity_not_sufficient: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    delayed_transport: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    improper_transport: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    improper_container: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    incomplete_details_in_form: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    accepted: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    accepted_with_remark: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    rejected: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    lab_remark: Mapped[str | None] = mapped_column(Text, nullable=True)

    receiver_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    receiver_signature_present: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    master_form: Mapped[MasterForm] = relationship(back_populates='pathology_hematology_form')
    tests: Mapped[list['PathologyHematologyTest']] = relationship(back_populates='pathology_form', cascade='all, delete-orphan')


class PathologyHematologyTest(Base):
    __tablename__ = 'pathology_hematology_tests'
    __table_args__ = (
        CheckConstraint("test_group IN ('24x7','routine_hours_only')"),
        CheckConstraint('is_selected IN (0,1)'),
        Index('idx_pathology_hematology_tests_pathology_id', 'pathology_id'),
    )

    pathology_test_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    pathology_id: Mapped[int] = mapped_column(ForeignKey('pathology_hematology_form.pathology_id', ondelete='CASCADE'), nullable=False)
    sr_no: Mapped[int | None] = mapped_column(Integer, nullable=True)
    test_name: Mapped[str] = mapped_column(String(255), nullable=False)
    test_group: Mapped[str] = mapped_column(String(32), nullable=False)
    is_selected: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    pathology_form: Mapped[PathologyHematologyForm] = relationship(back_populates='tests')


class ClinicalChemistryForm(Base):
    __tablename__ = 'clinical_chemistry_form'
    __table_args__ = (
        CheckConstraint('sender_signature_present IN (0,1)'),
        CheckConstraint('rejection_improper_containers IN (0,1)'),
        CheckConstraint('rejection_incomplete_details_in_form IN (0,1)'),
        CheckConstraint('rejection_quantity_not_sufficient IN (0,1)'),
        CheckConstraint('rejection_delayed_or_improper_transport IN (0,1)'),
        CheckConstraint('rejection_stale_blood IN (0,1)'),
        CheckConstraint('rejection_grossly_hemolysed IN (0,1)'),
    )

    chemistry_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    master_id: Mapped[int] = mapped_column(ForeignKey('master_forms.master_id', ondelete='CASCADE'), nullable=False, unique=True)

    specimen_type_other_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    cause_of_urgency: Mapped[str | None] = mapped_column(Text, nullable=True)
    other_investigation_text: Mapped[str | None] = mapped_column(Text, nullable=True)

    sender_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    sender_signature_present: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    sender_phone_number: Mapped[str | None] = mapped_column(String(64), nullable=True)

    clinician_patient_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    clinician_mrd_no: Mapped[str | None] = mapped_column(String(128), nullable=True)
    clinician_laboratory_accession_no: Mapped[str | None] = mapped_column(String(128), nullable=True)

    rejection_improper_containers: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    rejection_incomplete_details_in_form: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    rejection_quantity_not_sufficient: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    rejection_delayed_or_improper_transport: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    rejection_stale_blood: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    rejection_grossly_hemolysed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    rejection_other_text: Mapped[str | None] = mapped_column(Text, nullable=True)

    master_form: Mapped[MasterForm] = relationship(back_populates='clinical_chemistry_form')
    tests: Mapped[list['ClinicalChemistryTest']] = relationship(back_populates='chemistry_form', cascade='all, delete-orphan')


class ClinicalChemistryTest(Base):
    __tablename__ = 'clinical_chemistry_tests'
    __table_args__ = (
        CheckConstraint('is_selected IN (0,1)'),
        Index('idx_clinical_chemistry_tests_chemistry_id', 'chemistry_id'),
    )

    chemistry_test_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    chemistry_id: Mapped[int] = mapped_column(ForeignKey('clinical_chemistry_form.chemistry_id', ondelete='CASCADE'), nullable=False)
    parameter_name: Mapped[str] = mapped_column(String(255), nullable=False)
    section_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_selected: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    chemistry_form: Mapped[ClinicalChemistryForm] = relationship(back_populates='tests')


class BloodRequestForm(Base):
    __tablename__ = 'blood_request_form'
    __table_args__ = (
        CheckConstraint('doctor_certified_sample_collected IN (0,1)'),
        CheckConstraint('doctor_signature_present IN (0,1)'),
        CheckConstraint('hospital_stamp_present IN (0,1)'),
    )

    blood_request_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    master_id: Mapped[int] = mapped_column(ForeignKey('master_forms.master_id', ondelete='CASCADE'), nullable=False, unique=True)

    hospital_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    ic_unit_doctor: Mapped[str | None] = mapped_column(Text, nullable=True)

    operative_procedure_date: Mapped[str | None] = mapped_column(String(64), nullable=True)
    operative_procedure_name: Mapped[str | None] = mapped_column(Text, nullable=True)

    hb_gm_percent: Mapped[str | None] = mapped_column(String(64), nullable=True)
    platelet_count_per_cumm: Mapped[str | None] = mapped_column(String(64), nullable=True)
    pt_aptt_seconds: Mapped[str | None] = mapped_column(String(64), nullable=True)
    bp_mmhg: Mapped[str | None] = mapped_column(String(64), nullable=True)
    urine_output_cc: Mapped[str | None] = mapped_column(String(64), nullable=True)

    known_blood_group: Mapped[str | None] = mapped_column(String(64), nullable=True)
    previous_transfusion_history: Mapped[str | None] = mapped_column(Text, nullable=True)
    transfusion_reaction_history: Mapped[str | None] = mapped_column(Text, nullable=True)
    pregnancy_stillbirth_abortion_hdfn_history: Mapped[str | None] = mapped_column(Text, nullable=True)

    doctor_certified_sample_collected: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    doctor_signature_present: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    doctor_name_contact: Mapped[str | None] = mapped_column(Text, nullable=True)
    doctor_reg_no: Mapped[str | None] = mapped_column(String(128), nullable=True)
    hospital_stamp_present: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    blood_centre_sample_received_time: Mapped[str | None] = mapped_column(String(64), nullable=True)
    blood_centre_sample_received_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    blood_centre_patient_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    blood_centre_reg_no: Mapped[str | None] = mapped_column(String(128), nullable=True)
    blood_centre_blood_group: Mapped[str | None] = mapped_column(String(64), nullable=True)

    special_tests_result: Mapped[str | None] = mapped_column(Text, nullable=True)
    special_tests_date: Mapped[str | None] = mapped_column(String(64), nullable=True)
    special_tests_time: Mapped[str | None] = mapped_column(String(64), nullable=True)

    master_form: Mapped[MasterForm] = relationship(back_populates='blood_request_form')
    request_types: Mapped[list['BloodRequestType']] = relationship(back_populates='blood_request', cascade='all, delete-orphan')
    component_requests: Mapped[list['BloodComponentRequest']] = relationship(back_populates='blood_request', cascade='all, delete-orphan')
    reserve_records: Mapped[list['BloodReserveRecord']] = relationship(back_populates='blood_request', cascade='all, delete-orphan')
    compatibility_test: Mapped['BloodCompatibilityTest | None'] = relationship(
        back_populates='blood_request', cascade='all, delete-orphan', uselist=False
    )
    issue_records: Mapped[list['BloodIssueRecord']] = relationship(back_populates='blood_request', cascade='all, delete-orphan')


class BloodRequestType(Base):
    __tablename__ = 'blood_request_types'
    __table_args__ = (
        CheckConstraint('is_selected IN (0,1)'),
        Index('idx_blood_request_types_blood_request_id', 'blood_request_id'),
    )

    request_type_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    blood_request_id: Mapped[int] = mapped_column(ForeignKey('blood_request_form.blood_request_id', ondelete='CASCADE'), nullable=False)
    request_type_name: Mapped[str] = mapped_column(String(128), nullable=False)
    is_selected: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    blood_request: Mapped[BloodRequestForm] = relationship(back_populates='request_types')


class BloodComponentRequest(Base):
    __tablename__ = 'blood_component_requests'
    __table_args__ = (
        CheckConstraint('is_requested IN (0,1)'),
        Index('idx_blood_component_requests_blood_request_id', 'blood_request_id'),
    )

    component_request_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    blood_request_id: Mapped[int] = mapped_column(ForeignKey('blood_request_form.blood_request_id', ondelete='CASCADE'), nullable=False)
    component_name: Mapped[str] = mapped_column(String(128), nullable=False)
    date_of_requirement: Mapped[str | None] = mapped_column(String(64), nullable=True)
    is_requested: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    blood_request: Mapped[BloodRequestForm] = relationship(back_populates='component_requests')


class BloodReserveRecord(Base):
    __tablename__ = 'blood_reserve_records'
    __table_args__ = (Index('idx_blood_reserve_records_blood_request_id', 'blood_request_id'),)

    reserve_record_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    blood_request_id: Mapped[int] = mapped_column(ForeignKey('blood_request_form.blood_request_id', ondelete='CASCADE'), nullable=False)
    line_no: Mapped[int | None] = mapped_column(Integer, nullable=True)
    units_text: Mapped[str | None] = mapped_column(String(128), nullable=True)
    reserve_date: Mapped[str | None] = mapped_column(String(64), nullable=True)
    replaced_bb_no: Mapped[str | None] = mapped_column(String(128), nullable=True)

    blood_request: Mapped[BloodRequestForm] = relationship(back_populates='reserve_records')


class BloodCompatibilityTest(Base):
    __tablename__ = 'blood_compatibility_tests'

    compatibility_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    blood_request_id: Mapped[int] = mapped_column(ForeignKey('blood_request_form.blood_request_id', ondelete='CASCADE'), nullable=False, unique=True)

    anti_a: Mapped[str | None] = mapped_column(String(64), nullable=True)
    anti_b: Mapped[str | None] = mapped_column(String(64), nullable=True)
    anti_ab: Mapped[str | None] = mapped_column(String(64), nullable=True)

    serum_a: Mapped[str | None] = mapped_column(String(64), nullable=True)
    serum_b: Mapped[str | None] = mapped_column(String(64), nullable=True)
    serum_o: Mapped[str | None] = mapped_column(String(64), nullable=True)

    rh_d1: Mapped[str | None] = mapped_column(String(64), nullable=True)
    rh_d2: Mapped[str | None] = mapped_column(String(64), nullable=True)
    rh_du: Mapped[str | None] = mapped_column(String(64), nullable=True)

    auto_control: Mapped[str | None] = mapped_column(String(64), nullable=True)
    final_blood_group: Mapped[str | None] = mapped_column(String(64), nullable=True)
    dat_result: Mapped[str | None] = mapped_column(String(64), nullable=True)
    iat_result: Mapped[str | None] = mapped_column(String(64), nullable=True)

    examined_by: Mapped[str | None] = mapped_column(String(255), nullable=True)

    blood_request: Mapped[BloodRequestForm] = relationship(back_populates='compatibility_test')


class BloodIssueRecord(Base):
    __tablename__ = 'blood_issue_records'
    __table_args__ = (Index('idx_blood_issue_records_blood_request_id', 'blood_request_id'),)

    issue_record_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    blood_request_id: Mapped[int] = mapped_column(ForeignKey('blood_request_form.blood_request_id', ondelete='CASCADE'), nullable=False)

    sr_no: Mapped[int | None] = mapped_column(Integer, nullable=True)
    record_date_time: Mapped[str | None] = mapped_column(String(64), nullable=True)

    unit_no: Mapped[str | None] = mapped_column(String(128), nullable=True)
    segment_no: Mapped[str | None] = mapped_column(String(128), nullable=True)
    blood_group_of_bag: Mapped[str | None] = mapped_column(String(64), nullable=True)
    blood_component_type_volume: Mapped[str | None] = mapped_column(String(128), nullable=True)

    crossmatch_saline_rt: Mapped[str | None] = mapped_column(String(64), nullable=True)
    crossmatch_ahg_37c: Mapped[str | None] = mapped_column(String(64), nullable=True)

    crossmatch_done_by_name_signature: Mapped[str | None] = mapped_column(Text, nullable=True)
    issue_date_time_sign: Mapped[str | None] = mapped_column(Text, nullable=True)

    blood_request: Mapped[BloodRequestForm] = relationship(back_populates='issue_records')
