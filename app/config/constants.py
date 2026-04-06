from enum import Enum


class StrEnum(str, Enum):
    pass


class Role(StrEnum):
    ADMIN = 'Admin'
    OPERATOR = 'Operator'


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
