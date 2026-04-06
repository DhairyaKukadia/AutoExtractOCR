from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class MasterFormPayload(BaseModel):
    form_type: Literal['pathology_hematology', 'clinical_chemistry', 'blood_request']
    source_file_name: str

    patient_name: str | None = None
    age: str | None = None
    sex: str | None = None
    age_sex_text: str | None = None
    registration_no: str | None = None
    mrd_no: str | None = None
    hospital_name: str | None = None
    ward_unit_opd: str | None = None
    doctor_name: str | None = None
    doctor_contact_no: str | None = None
    sample_or_specimen_type: str | None = None
    collection_date: str | None = None
    collection_time: str | None = None
    collection_am_pm: str | None = None
    clinical_note_text: str | None = None
    diagnosis: str | None = None
    remarks: str | None = None
    urgency_type: Literal['urgent', 'routine'] | None = None
    lab_id: str | None = None
    laboratory_accession_no: str | None = None
    bbr_no: str | None = None
    raw_ocr_text: str | None = None
    ocr_confidence: float | None = None
    review_status: Literal['pending', 'reviewed', 'approved', 'rejected'] = 'pending'


class PathologyHematologyTestPayload(BaseModel):
    sr_no: int | None = None
    test_name: str
    test_group: Literal['24x7', 'routine_hours_only']
    is_selected: int = Field(default=0, ge=0, le=1)


class PathologyHematologyDetailPayload(BaseModel):
    recent_blood_transfusion_flag: Literal['yes', 'no'] | None = None
    recent_blood_transfusion_details: str | None = None
    hemoglobinopathy_family_history_flag: Literal['yes', 'no'] | None = None
    hemoglobinopathy_family_history_details: str | None = None
    sample_type_other_text: str | None = None
    body_fluid_source: str | None = None
    critical_report_phone: str | None = None
    sender_name: str | None = None
    sender_role: str | None = None
    sender_signature_present: int = Field(default=0, ge=0, le=1)
    lab_receipt_time: str | None = None
    lab_receipt_am_pm: str | None = None
    lab_date: str | None = None
    quality_ok: int = Field(default=0, ge=0, le=1)
    hemolysed: int = Field(default=0, ge=0, le=1)
    quantity_not_sufficient: int = Field(default=0, ge=0, le=1)
    delayed_transport: int = Field(default=0, ge=0, le=1)
    improper_transport: int = Field(default=0, ge=0, le=1)
    improper_container: int = Field(default=0, ge=0, le=1)
    incomplete_details_in_form: int = Field(default=0, ge=0, le=1)
    accepted: int = Field(default=0, ge=0, le=1)
    accepted_with_remark: int = Field(default=0, ge=0, le=1)
    rejected: int = Field(default=0, ge=0, le=1)
    lab_remark: str | None = None
    receiver_name: str | None = None
    receiver_signature_present: int = Field(default=0, ge=0, le=1)
    tests: list[PathologyHematologyTestPayload] = Field(default_factory=list)


class ClinicalChemistryTestPayload(BaseModel):
    parameter_name: str
    section_name: str | None = None
    is_selected: int = Field(default=0, ge=0, le=1)


class ClinicalChemistryDetailPayload(BaseModel):
    specimen_type_other_text: str | None = None
    cause_of_urgency: str | None = None
    other_investigation_text: str | None = None
    sender_name: str | None = None
    sender_signature_present: int = Field(default=0, ge=0, le=1)
    sender_phone_number: str | None = None
    clinician_patient_name: str | None = None
    clinician_mrd_no: str | None = None
    clinician_laboratory_accession_no: str | None = None
    rejection_improper_containers: int = Field(default=0, ge=0, le=1)
    rejection_incomplete_details_in_form: int = Field(default=0, ge=0, le=1)
    rejection_quantity_not_sufficient: int = Field(default=0, ge=0, le=1)
    rejection_delayed_or_improper_transport: int = Field(default=0, ge=0, le=1)
    rejection_stale_blood: int = Field(default=0, ge=0, le=1)
    rejection_grossly_hemolysed: int = Field(default=0, ge=0, le=1)
    rejection_other_text: str | None = None
    tests: list[ClinicalChemistryTestPayload] = Field(default_factory=list)


class BloodRequestTypePayload(BaseModel):
    request_type_name: str
    is_selected: int = Field(default=0, ge=0, le=1)


class BloodComponentRequestPayload(BaseModel):
    component_name: str
    date_of_requirement: str | None = None
    is_requested: int = Field(default=0, ge=0, le=1)


class BloodReserveRecordPayload(BaseModel):
    line_no: int | None = None
    units_text: str | None = None
    reserve_date: str | None = None
    replaced_bb_no: str | None = None


class BloodCompatibilityPayload(BaseModel):
    anti_a: str | None = None
    anti_b: str | None = None
    anti_ab: str | None = None
    serum_a: str | None = None
    serum_b: str | None = None
    serum_o: str | None = None
    rh_d1: str | None = None
    rh_d2: str | None = None
    rh_du: str | None = None
    auto_control: str | None = None
    final_blood_group: str | None = None
    dat_result: str | None = None
    iat_result: str | None = None
    examined_by: str | None = None


class BloodIssueRecordPayload(BaseModel):
    sr_no: int | None = None
    record_date_time: str | None = None
    unit_no: str | None = None
    segment_no: str | None = None
    blood_group_of_bag: str | None = None
    blood_component_type_volume: str | None = None
    crossmatch_saline_rt: str | None = None
    crossmatch_ahg_37c: str | None = None
    crossmatch_done_by_name_signature: str | None = None
    issue_date_time_sign: str | None = None


class BloodRequestDetailPayload(BaseModel):
    hospital_text: str | None = None
    ic_unit_doctor: str | None = None
    operative_procedure_date: str | None = None
    operative_procedure_name: str | None = None
    hb_gm_percent: str | None = None
    platelet_count_per_cumm: str | None = None
    pt_aptt_seconds: str | None = None
    bp_mmhg: str | None = None
    urine_output_cc: str | None = None
    known_blood_group: str | None = None
    previous_transfusion_history: str | None = None
    transfusion_reaction_history: str | None = None
    pregnancy_stillbirth_abortion_hdfn_history: str | None = None
    doctor_certified_sample_collected: int = Field(default=0, ge=0, le=1)
    doctor_signature_present: int = Field(default=0, ge=0, le=1)
    doctor_name_contact: str | None = None
    doctor_reg_no: str | None = None
    hospital_stamp_present: int = Field(default=0, ge=0, le=1)
    blood_centre_sample_received_time: str | None = None
    blood_centre_sample_received_by: str | None = None
    blood_centre_patient_name: str | None = None
    blood_centre_reg_no: str | None = None
    blood_centre_blood_group: str | None = None
    special_tests_result: str | None = None
    special_tests_date: str | None = None
    special_tests_time: str | None = None
    request_types: list[BloodRequestTypePayload] = Field(default_factory=list)
    component_requests: list[BloodComponentRequestPayload] = Field(default_factory=list)
    reserve_records: list[BloodReserveRecordPayload] = Field(default_factory=list)
    compatibility_test: BloodCompatibilityPayload | None = None
    issue_records: list[BloodIssueRecordPayload] = Field(default_factory=list)
