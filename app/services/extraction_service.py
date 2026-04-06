import re


class ExtractionService:
    def parse(self, text: str, template_name: str | None = None) -> dict[str, str]:
        extracted = {
            'patient_name': self._extract(text, [r"Patient(?:'s)?\s*Name\s*[:\-]\s*(.+)", r'PATIENT\s*NAME\s*[:\-]\s*(.+)']),
            'age_sex': self._extract(text, [r'Age\s*&\s*Sex\s*[:\-]\s*(.+)', r'AGE\s*/\s*GENDER\s*[:\-]\s*(.+)']),
            'registration_no': self._extract(text, [r'REGISTRATION\s*[:\-]?\s*([^\n]+)', r'Reg\.\s*No\.?\s*[:\-]?\s*([^\n]+)']),
            'mrd_no': self._extract(text, [r'MRD\s*No\.?\s*[:\-]?\s*([^\n]+)', r'MRD\s*No\s*[:\-]?\s*([^\n]+)']),
            'bbr_no': self._extract(text, [r'BBR\s*NO\s*[:\-]?\s*([^\n]+)', r'BBR\s*No\.?\s*[:\-]?\s*([^\n]+)']),
            'ward_unit': self._extract(text, [r'Ward/Unit/OPD\.?\s*[:\-]\s*(.+)', r'WARD\s*[:\-]\s*(.+)']),
            'doctor_name': self._extract(text, [r'Referring\s*Dr\.?\s*\/?\s*Name\s*[:\-]\s*(.+)', r"Doctor's\s*Name\s*&\s*Contact\s*No\s*[:\-]\s*(.+)"]),
            'doctor_contact_no': self._extract(text, [r"REFERRING\s*Dr.?\s*CONTACT\s*NO\.?\(?[:\-]?\)?\s*([^\n]+)", r'Sender\'s\s*phone\s*number[^:]*:\s*([^\n]+)']),
            'sample_or_specimen_type': self._extract(text, [r'Specimen\s*type\s*sent\s*[:\-]\s*(.+)', r'SAMPLE\s*TYPE\s*SENT\s*[:\-]\s*(.+)']),
        }

        extracted['form_type'] = self._infer_form_type(text, template_name)
        extracted['patient_identifier'] = self._first_non_empty(
            extracted['mrd_no'],
            extracted['registration_no'],
            extracted['bbr_no'],
            self._extract(text, [r'(?:Patient\s*(?:ID|Identifier)|MRN)\s*[:\-]?\s*([A-Za-z0-9\-\/]+)']),
        )

        return extracted

    def _infer_form_type(self, text: str, template_name: str | None) -> str:
        explicit = self._extract(text, [r'Form\s*Type\s*[:\-]\s*(.+)', r'Prescription\s*Type\s*[:\-]\s*(.+)'])
        if explicit:
            return explicit
        if template_name:
            return template_name

        upper = text.upper()
        if 'CLINICAL PATHOLOGY' in upper or 'HAEMATOLOGY' in upper:
            return 'pathology_hematology'
        if 'CLINICAL CHEMISTRY' in upper:
            return 'clinical_chemistry'
        if 'BLOOD REQUEST FORM' in upper or 'BLOOD CENTRE' in upper:
            return 'blood_request'

        return ''

    def _extract(self, text: str, patterns: list[str]) -> str:
        for pattern in patterns:
            match = re.search(pattern, text, flags=re.IGNORECASE)
            if match:
                return self._clean(match.group(1))
        return ''

    @staticmethod
    def _clean(value: str) -> str:
        value = value.strip()
        value = re.sub(r'\s{2,}', ' ', value)
        return value.strip(' .')

    @staticmethod
    def _first_non_empty(*values: str) -> str:
        for value in values:
            if value:
                return value
        return ''
