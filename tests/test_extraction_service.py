from app.services.extraction_service import ExtractionService


def test_generic_extraction_parse():
    service = ExtractionService()
    text = (
        'Patient Name: jane   DOE\n'
        'Patient ID: P-100\n'
        'Form Type: registration\n'
        'MRD No: MRD/200\n'
        'Doctor Name: dr aLiCe smith\n'
        'Laboratory Accession: LAB-9'
    )
    fields = service.parse(text)
    assert fields['patient_name'] == 'Jane Doe'
    assert fields['patient_identifier'] == 'P-100'
    assert fields['form_type'] == 'Registration'
    assert fields['mrd_no'] == 'MRD/200'
    assert fields['doctor_name'] == 'Dr Alice Smith'
    assert fields['laboratory_accession_no'] == 'LAB-9'


def test_template_aware_extraction_parse():
    service = ExtractionService()
    text = 'Patient Name: Jane Doe\nMRN: M-200\nPrescription Type: Chronic'
    fields = service.parse(text, template_name='Prescription')
    assert fields['patient_identifier'] == 'M-200'
    assert fields['form_type'] == 'Chronic'


def test_generic_extraction_missing_and_noisy_values():
    service = ExtractionService()
    text = 'Patient ID: ID-99! @\nForm Type: emergency intake\nSome other line'

    fields = service.parse(text)

    assert fields['patient_name'] == ''
    assert fields['doctor_name'] == ''
    assert fields['mrd_no'] == ''
    assert fields['patient_identifier'] == 'ID-99'
    assert fields['form_type'] == 'Emergency Intake'


def test_template_resolution_falls_back_to_form_category():
    service = ExtractionService()
    text = 'Patient Name: Jane Doe\nMRN: M-200\nPrescription Type: Chronic'
    fields = service.parse(text, template_name='', form_category='Prescription')
    assert fields['patient_identifier'] == 'M-200'
    assert fields['form_type'] == 'Chronic'
