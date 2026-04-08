import re

DEFAULT_FORM_CATEGORY_TO_TABLE = {
    'Laboratory Request Form - Clinical Pathology / Haematology': 'pathology_hematology_form',
    'Clinical Chemistry Laboratory Test Requisition Form': 'clinical_chemistry_form',
    'Blood Request Form': 'blood_request_form',
}

DEFAULT_CATEGORY_FIELD_LAYOUT = {
    'Laboratory Request Form - Clinical Pathology / Haematology': [
        'patient_name', 'age_gender', 'registration_no', 'referring_doctor_name',
        'referring_doctor_contact', 'relevant_clinical_details', 'sample_type_sent', 'investigations_required',
    ],
    'Clinical Chemistry Laboratory Test Requisition Form': [
        'patient_name', 'age_sex', 'mrd_no', 'ward_unit_opd', 'referring_doctor',
        'specimen_type', 'provisional_diagnosis', 'investigations_required',
    ],
    'Blood Request Form': [
        'patient_name', 'age', 'sex', 'hospital', 'registration_no', 'ward',
        'clinical_diagnosis', 'blood_group', 'request_type', 'doctor_name_contact', 'bbr_no',
    ],
}

try:
    import app.config.constants as app_constants
    CATEGORY_FIELD_LAYOUT = getattr(app_constants, 'CATEGORY_FIELD_LAYOUT', DEFAULT_CATEGORY_FIELD_LAYOUT)
    FORM_CATEGORY_TO_TABLE = getattr(app_constants, 'FORM_CATEGORY_TO_TABLE', DEFAULT_FORM_CATEGORY_TO_TABLE)
except Exception:
    CATEGORY_FIELD_LAYOUT = DEFAULT_CATEGORY_FIELD_LAYOUT
    FORM_CATEGORY_TO_TABLE = DEFAULT_FORM_CATEGORY_TO_TABLE
