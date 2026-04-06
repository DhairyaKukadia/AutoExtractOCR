"""Seed script inserting one example row for each selected form type."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.data.database import SessionLocal, init_db
from app.data.form_payloads import (
    BloodCompatibilityPayload,
    BloodComponentRequestPayload,
    BloodIssueRecordPayload,
    BloodRequestDetailPayload,
    BloodRequestTypePayload,
    BloodReserveRecordPayload,
    ClinicalChemistryDetailPayload,
    ClinicalChemistryTestPayload,
    MasterFormPayload,
    PathologyHematologyDetailPayload,
    PathologyHematologyTestPayload,
)
from app.services.form_ingestion_service import FormIngestionService


def main() -> None:
    init_db()
    session = SessionLocal()
    service = FormIngestionService(session)

    pathology_master = MasterFormPayload(
        form_type='pathology_hematology',
        source_file_name='pathology_form_sample.png',
        patient_name='Ravi Kumar',
        mrd_no='MRD-1001',
        doctor_name='Dr. Sharma',
        sample_or_specimen_type='Blood',
    )
    pathology_detail = PathologyHematologyDetailPayload(
        sender_name='Nurse Anita',
        sender_role='Nurse',
        sender_signature_present=1,
        tests=[
            PathologyHematologyTestPayload(sr_no=1, test_name='CBC', test_group='24x7', is_selected=1),
            PathologyHematologyTestPayload(sr_no=2, test_name='ESR', test_group='routine_hours_only', is_selected=1),
        ],
    )

    chemistry_master = MasterFormPayload(
        form_type='clinical_chemistry',
        source_file_name='chemistry_form_sample.png',
        patient_name='Seema Patel',
        mrd_no='MRD-2002',
        laboratory_accession_no='LAB-ACC-55',
    )
    chemistry_detail = ClinicalChemistryDetailPayload(
        sender_name='Dr. Mehta',
        sender_signature_present=1,
        tests=[
            ClinicalChemistryTestPayload(parameter_name='Serum Creatinine', section_name='Renal', is_selected=1),
            ClinicalChemistryTestPayload(parameter_name='Urea', section_name='Renal', is_selected=1),
        ],
    )

    blood_master = MasterFormPayload(
        form_type='blood_request',
        source_file_name='blood_request_sample.png',
        patient_name='Kiran Rao',
        mrd_no='MRD-3003',
        bbr_no='BBR-7788',
    )
    blood_detail = BloodRequestDetailPayload(
        doctor_signature_present=1,
        hospital_stamp_present=1,
        request_types=[BloodRequestTypePayload(request_type_name='Whole Blood', is_selected=1)],
        component_requests=[
            BloodComponentRequestPayload(component_name='Packed RBC', date_of_requirement='2026-04-04', is_requested=1)
        ],
        reserve_records=[BloodReserveRecordPayload(line_no=1, units_text='2 units', reserve_date='2026-04-04')],
        compatibility_test=BloodCompatibilityPayload(final_blood_group='B+', examined_by='Technician A'),
        issue_records=[
            BloodIssueRecordPayload(sr_no=1, unit_no='UNIT-101', blood_group_of_bag='B+', crossmatch_saline_rt='Compatible')
        ],
    )

    for master, detail in [
        (pathology_master, pathology_detail),
        (chemistry_master, chemistry_detail),
        (blood_master, blood_detail),
    ]:
        if master.form_type == 'pathology_hematology':
            master_id, record_uid = service.insert_pathology_hematology(master, detail)
        elif master.form_type == 'clinical_chemistry':
            master_id, record_uid = service.insert_clinical_chemistry(master, detail)
        else:
            master_id, record_uid = service.insert_blood_request(master, detail)

        print(f'Inserted {master.form_type}: master_id={master_id}, record_uid={record_uid}')

    session.close()


if __name__ == '__main__':
    main()
