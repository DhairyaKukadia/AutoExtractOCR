from enum import StrEnum


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
    'Patient Registration',
    'Prescription',
    'Lab Request',
    'Lab Report Intake',
    'Insurance Form',
    'Consent Form',
    'Admission Form',
    'Discharge Summary Intake',
    'Other',
]
