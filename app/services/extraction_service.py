import re


class ExtractionService:
    generic_patterns = {
        'patient_name': r'Patient\s*Name[:\-]?\s*(.+)',
        'patient_identifier': r'(Patient\s*(ID|Identifier)|MRN)[:\-]?\s*([A-Za-z0-9\-]+)',
        'form_type': r'Form\s*Type[:\-]?\s*(.+)',
        'mrd_no': r'MRD\s*(No|#)?[:\-]?\s*([A-Za-z0-9\-\/]+)',
        'doctor_name': r'(Doctor|Consultant)\s*Name[:\-]?\s*(.+)',
        'laboratory_accession_no': r'(Laboratory\s*Accession|Lab\s*ID)[:\-]?\s*([A-Za-z0-9\-\/]+)',
    }

    template_patterns = {
        'Prescription': {
            'patient_name': r'Patient\s*Name[:\-]?\s*(.+)',
            'patient_identifier': r'MRN[:\-]?\s*([A-Za-z0-9\-]+)',
            'form_type': r'Prescription\s*Type[:\-]?\s*(.+)',
        },
        'Lab Request': {
            'patient_name': r'Patient\s*Name[:\-]?\s*(.+)',
            'patient_identifier': r'(Lab\s*ID|Patient\s*ID)[:\-]?\s*([A-Za-z0-9\-]+)',
            'form_type': r'Test\s*Type[:\-]?\s*(.+)',
        },
    }

    def parse(self, text: str, template_name: str = '', form_category: str = '') -> dict[str, str]:
        patterns = self._resolve_patterns(template_name, form_category)
        fields: dict[str, str] = {}
        for key, pattern in patterns.items():
            match = re.search(pattern, text, flags=re.IGNORECASE)
            if not match:
                fields[key] = ''
                continue

            if key == 'patient_identifier' and len(match.groups()) >= 3:
                fields[key] = match.group(3).strip()
            elif key in {'patient_identifier', 'mrd_no', 'laboratory_accession_no', 'doctor_name'} and len(match.groups()) >= 1:
                fields[key] = match.group(len(match.groups())).strip()
            else:
                fields[key] = match.group(1).strip()
        return self._normalize_fields(fields)

    def _normalize_fields(self, fields: dict[str, str]) -> dict[str, str]:
        normalized = dict(fields)
        if normalized.get('patient_name'):
            normalized['patient_name'] = self._titleize_name(normalized['patient_name'])
        for key in ('patient_identifier', 'mrd_no', 'laboratory_accession_no'):
            value = normalized.get(key, '')
            normalized[key] = re.sub(r'[^A-Za-z0-9\-/]', '', value)
        if normalized.get('doctor_name'):
            normalized['doctor_name'] = self._titleize_name(normalized['doctor_name'])
        if normalized.get('form_type'):
            normalized['form_type'] = normalized['form_type'].strip().title()
        return normalized

    @staticmethod
    def _titleize_name(value: str) -> str:
        tokens = re.sub(r'\s+', ' ', value).strip().split(' ')
        return ' '.join(token.capitalize() for token in tokens if token)

    def _resolve_patterns(self, template_name: str, form_category: str) -> dict[str, str]:
        if template_name in self.template_patterns:
            return self.template_patterns[template_name]
        if form_category in self.template_patterns:
            return self.template_patterns[form_category]
        return self.generic_patterns
