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


FORM_CATEGORIES = [
    'Pathology / Haematology Request',
    'Clinical Chemistry Requisition',
    'Blood Request Form',
]


FORM_CATEGORY_TO_TYPE = {
    'Pathology / Haematology Request': 'pathology_hematology',
    'Clinical Chemistry Requisition': 'clinical_chemistry',
    'Blood Request Form': 'blood_request',
}


OCR_LAYOUT_FIELDS = [
    'patient_name',
    'age_sex',
    'registration_no',
    'mrd_no',
    'bbr_no',
    'ward_unit',
    'doctor_name',
    'doctor_contact_no',
    'sample_or_specimen_type',
    'form_type',
    'patient_identifier',
]


FORM_CATEGORY_TO_TYPE = {
    'Pathology / Haematology Request': 'pathology_hematology',
    'Clinical Chemistry Requisition': 'clinical_chemistry',
    'Blood Request Form': 'blood_request',
}
