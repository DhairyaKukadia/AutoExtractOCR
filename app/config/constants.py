from enum import Enum


class StrEnum(str, Enum):
    pass


class Role(StrEnum):
    ADMIN = 'Admin'
    OPERATOR = 'Operator'
    REVIEWER = 'Reviewer'


class ReviewStatus(StrEnum):
    DRAFT = 'draft'
    EXTRACTED = 'extracted'
    REVIEWED = 'reviewed'
    APPROVED = 'approved'
    REJECTED = 'rejected'


FORM_TYPES = [
    'Laboratory Request Form - Clinical Pathology / Haematology',
    'Clinical Chemistry Laboratory Test Requisition Form',
    'Blood Request Form',
]

FORM_CATEGORIES = FORM_TYPES

FORM_CATEGORY_TO_TABLE = {
    'Laboratory Request Form - Clinical Pathology / Haematology': 'pathology_hematology_form',
    'Clinical Chemistry Laboratory Test Requisition Form': 'clinical_chemistry_form',
    'Blood Request Form': 'blood_request_form',
}

CATEGORY_FIELD_LAYOUT = {
    'Laboratory Request Form - Clinical Pathology / Haematology': [
        'patient_name',
        'age_gender',
        'registration_no',
        'referring_doctor_name',
        'referring_doctor_contact',
        'relevant_clinical_details',
        'sample_type_sent',
        'investigations_required',
    ],
    'Clinical Chemistry Laboratory Test Requisition Form': [
        'patient_name',
        'age_sex',
        'mrd_no',
        'ward_unit_opd',
        'referring_doctor',
        'specimen_type',
        'provisional_diagnosis',
        'investigations_required',
    ],
    'Blood Request Form': [
        'patient_name',
        'age',
        'sex',
        'hospital',
        'registration_no',
        'ward',
        'clinical_diagnosis',
        'blood_group',
        'request_type',
        'doctor_name_contact',
        'bbr_no',
    ],
}

ALLOWED_STATUS_TRANSITIONS = {
    'draft': {'extracted'},
    'extracted': {'reviewed', 'rejected'},
    'reviewed': {'approved', 'rejected'},
    'approved': set(),
    'rejected': set(),
}

# Backward compatibility alias used by extraction service.
FORM_CATEGORY_TO_TYPE = FORM_CATEGORY_TO_TABLE
