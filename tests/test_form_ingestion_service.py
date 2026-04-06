import pytest
from sqlalchemy.exc import IntegrityError

from app.data.form_models import (
    BloodCompatibilityTest,
    BloodComponentRequest,
    BloodIssueRecord,
    BloodRequestType,
    BloodReserveRecord,
    MasterForm,
    PathologyHematologyForm,
    PathologyHematologyTest,
)
from app.data.form_payloads import (
    BloodCompatibilityPayload,
    BloodComponentRequestPayload,
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
from tests.conftest import make_test_session


def test_insert_pathology_form_and_search_helpers():
    session = make_test_session()
    service = FormIngestionService(session)

    master = MasterFormPayload(
        form_type='pathology_hematology',
        source_file_name='path.png',
        patient_name='Test Patient',
        mrd_no='MRD-01',
    )
    detail = PathologyHematologyDetailPayload(
        tests=[PathologyHematologyTestPayload(test_name='CBC', test_group='24x7', is_selected=1)]
    )

    master_id, record_uid = service.insert_pathology_hematology(master, detail)

    assert master_id > 0
    assert record_uid
    assert len(service.search_by_patient_name('Test')) == 1
    assert len(service.search_by_mrd_no('MRD-01')) == 1
    assert len(service.search_by_form_type('pathology_hematology')) == 1


def test_insert_chemistry_and_blood_forms():
    session = make_test_session()
    service = FormIngestionService(session)

    chem_master = MasterFormPayload(form_type='clinical_chemistry', source_file_name='chem.png', patient_name='C1')
    chem_detail = ClinicalChemistryDetailPayload(
        tests=[ClinicalChemistryTestPayload(parameter_name='Urea', is_selected=1)]
    )
    blood_master = MasterFormPayload(form_type='blood_request', source_file_name='blood.png', patient_name='B1')
    blood_detail = BloodRequestDetailPayload(
        request_types=[BloodRequestTypePayload(request_type_name='Whole Blood', is_selected=1)],
        component_requests=[BloodComponentRequestPayload(component_name='Packed RBC', is_requested=1)],
        reserve_records=[BloodReserveRecordPayload(line_no=1, units_text='1', reserve_date='2026-04-06')],
        compatibility_test=BloodCompatibilityPayload(final_blood_group='O+', examined_by='Tech'),
        issue_records=[],
    )

    chem_id, _ = service.insert_clinical_chemistry(chem_master, chem_detail)
    blood_id, _ = service.insert_blood_request(blood_master, blood_detail)

    assert chem_id > 0
    assert blood_id > 0
    assert session.query(MasterForm).count() == 2

    blood_master = session.query(MasterForm).filter_by(master_id=blood_id).one()
    blood_request_id = blood_master.blood_request_form.blood_request_id
    assert session.query(BloodRequestType).filter_by(blood_request_id=blood_request_id).count() == 1
    assert session.query(BloodComponentRequest).filter_by(blood_request_id=blood_request_id).count() == 1
    assert session.query(BloodReserveRecord).filter_by(blood_request_id=blood_request_id).count() == 1
    assert session.query(BloodCompatibilityTest).filter_by(blood_request_id=blood_request_id).count() == 1
    assert session.query(BloodIssueRecord).filter_by(blood_request_id=blood_request_id).count() == 0


def test_insert_pathology_form_with_invalid_form_type_raises_value_error():
    session = make_test_session()
    service = FormIngestionService(session)

    master = MasterFormPayload(
        form_type='clinical_chemistry',
        source_file_name='path.png',
        patient_name='Mismatch',
        mrd_no='MRD-02',
    )
    detail = PathologyHematologyDetailPayload(
        tests=[PathologyHematologyTestPayload(test_name='CBC', test_group='24x7', is_selected=1)]
    )

    with pytest.raises(ValueError, match='pathology_hematology'):
        service.insert_pathology_hematology(master, detail)


def test_insert_pathology_form_rollback_on_detail_error():
    session = make_test_session()
    service = FormIngestionService(session)

    master = MasterFormPayload(
        form_type='pathology_hematology',
        source_file_name='path.png',
        patient_name='Rollback Patient',
        mrd_no='MRD-03',
    )
    bad_test = PathologyHematologyTestPayload.model_construct(
        sr_no=1,
        test_name='CBC',
        test_group='invalid_group',
        is_selected=1,
    )
    bad_detail = PathologyHematologyDetailPayload.model_construct(
        tests=[bad_test],
        sender_signature_present=0,
        quality_ok=0,
        hemolysed=0,
        quantity_not_sufficient=0,
        delayed_transport=0,
        improper_transport=0,
        improper_container=0,
        incomplete_details_in_form=0,
        accepted=0,
        accepted_with_remark=0,
        rejected=0,
        receiver_signature_present=0,
    )

    with pytest.raises(IntegrityError):
        service.insert_pathology_hematology(master, bad_detail)

    assert session.query(MasterForm).count() == 0
    assert session.query(PathologyHematologyForm).count() == 0
    assert session.query(PathologyHematologyTest).count() == 0
