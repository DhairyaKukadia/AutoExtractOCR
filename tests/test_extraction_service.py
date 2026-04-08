from app.services.extraction_service import ExtractionService


def test_generic_extraction_parse():
    service = ExtractionService()
    text = 'Patient Name: Jane Doe\nPatient ID: P-100\nForm Type: Registration'
    fields = service.parse(text)
    assert fields['patient_name'] == 'Jane Doe'
    assert fields['patient_identifier'] == 'P-100'
    assert fields['form_type'] == 'Registration'


def test_template_aware_extraction_parse():
    service = ExtractionService()
    text = 'Patient Name: Jane Doe\nMRN: M-200\nPrescription Type: Chronic'
    fields = service.parse(text, template_name='Prescription')
    assert fields['patient_identifier'] == 'M-200'
    assert fields['form_type'] == 'Chronic'
