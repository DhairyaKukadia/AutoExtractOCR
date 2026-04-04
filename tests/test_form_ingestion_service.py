from app.data.form_models import MasterForm
from app.data.form_payloads import (
    BloodRequestDetailPayload,
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
    blood_detail = BloodRequestDetailPayload()

    chem_id, _ = service.insert_clinical_chemistry(chem_master, chem_detail)
    blood_id, _ = service.insert_blood_request(blood_master, blood_detail)

    assert chem_id > 0
    assert blood_id > 0
    assert session.query(MasterForm).count() == 2
