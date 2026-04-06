import re

import app.config.constants as app_constants

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
        'patient_name', 'age_sex', 'mrd_no', 'ward_unit_opd', 'referring_doctor', 'specimen_type',
        'provisional_diagnosis', 'investigations_required',
    ],
    'Blood Request Form': [
        'patient_name', 'age', 'sex', 'hospital', 'registration_no', 'ward', 'clinical_diagnosis',
        'blood_group', 'request_type', 'doctor_name_contact', 'bbr_no',
    ],
}

CATEGORY_FIELD_LAYOUT = getattr(app_constants, 'CATEGORY_FIELD_LAYOUT', DEFAULT_CATEGORY_FIELD_LAYOUT)
FORM_CATEGORY_TO_TABLE = getattr(app_constants, 'FORM_CATEGORY_TO_TABLE', DEFAULT_FORM_CATEGORY_TO_TABLE)


class ParserService:
    """Regex + keyword mapper aligned to the three uploaded lab form names."""

    KEY_PATTERNS = {
        'patient_name': [r"Patient(?:'s)?\s*Name\s*[:\-]\s*(.+)", r'PATIENT\s*NAME\s*[:\-]\s*(.+)', r'Name\s*[:\-]\s*(.+)'],
        'age_gender': [r'AGE\s*/\s*GENDER\s*[:\-]\s*(.+)'],
        'age_sex': [r'Age\s*&\s*Sex\s*[:\-]\s*(.+)'],
        'age': [r'Age\s*[:\-]\s*(\d{1,3})'],
        'sex': [r'Sex\s*[:\-]\s*(Male|Female|Other)'],
        'registration_no': [r'REGISTRATION\s*[:\-]?\s*([^\n]+)', r'Reg\.\s*No\.?\s*[:\-]?\s*([^\n]+)'],
        'mrd_no': [r'MRD\s*No\.?\s*[:\-]?\s*([^\n]+)'],
        'bbr_no': [r'BBR\s*NO\s*[:\-]?\s*([^\n]+)'],
        'ward_unit_opd': [r'Ward/Unit/OPD\.?\s*[:\-]\s*(.+)'],
        'ward': [r'Ward\s*[:\-]\s*(.+)'],
        'hospital': [r'Hospital\s*[:\-]\s*(.+)'],
        'referring_doctor_name': [r'Referring\s*Dr\.?\s*\/?\s*Name\s*[:\-]\s*(.+)'],
        'referring_doctor_contact': [r'REFERRING\s*Dr.?\s*CONTACT\s*NO\.?\(?[:\-]?\)?\s*([^\n]+)'],
        'referring_doctor': [r'Ref\s*Dr\.?\s*[:\-]\s*(.+)', r'Referring\s*Doctor\s*[:\-]\s*(.+)'],
        'doctor_name_contact': [r"Doctor's\s*Name\s*&\s*Contact\s*No\s*[:\-]\s*(.+)"],
        'relevant_clinical_details': [r'RELEVANT\s*CLINICAL\s*DETAILS\s*[:\-]\s*(.+)'],
        'sample_type_sent': [r'SAMPLE\s*TYPE\s*SENT\s*[:\-]\s*(.+)'],
        'specimen_type': [r'Specimen\s*type\s*sent\s*[:\-]\s*(.+)'],
        'provisional_diagnosis': [r'Provisional\s*Diagnosis\s*[:\-]\s*(.+)'],
        'clinical_diagnosis': [r'Clinical\s*Diagnosis\s*[:\-]\s*(.+)'],
        'blood_group': [r'Blood\s*Group\s*if\s*known\s*[:\-]\s*(.+)'],
        'request_type': [r'Type\s*of\s*Request.*[:\-]\s*(.+)'],
        'investigations_required': [r'Investigation(?:s)?\s*required\s*[:\-]\s*(.+)', r'INVESTIGATION\s*REQUIRED\s*[:\-]\s*(.+)'],
    }

    def fields_for_category(self, category: str) -> list[str]:
        return list(CATEGORY_FIELD_LAYOUT.get(category, []))

    def map_to_structured(self, text: str, category: str) -> dict[str, str]:
        fields = self.fields_for_category(category)
        extracted = {field: self._extract(text, self.KEY_PATTERNS.get(field, [])) for field in fields}
        extracted['__target_table'] = FORM_CATEGORY_TO_TABLE.get(category, '')
        extracted['__category'] = category
        return extracted

    @staticmethod
    def _extract(text: str, patterns: list[str]) -> str:
        for pattern in patterns:
            match = re.search(pattern, text, flags=re.IGNORECASE)
            if match:
                return re.sub(r'\s{2,}', ' ', match.group(1).strip()).strip(' .')
        return ''
