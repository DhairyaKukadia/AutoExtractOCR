import re


class ExtractionService:
    generic_patterns = {
        'patient_name': r'Patient\s*Name[:\-]?\s*(.+)',
        'patient_identifier': r'(Patient\s*(ID|Identifier)|MRN)[:\-]?\s*([A-Za-z0-9\-]+)',
        'form_type': r'Form\s*Type[:\-]?\s*(.+)',
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
            elif key == 'patient_identifier' and len(match.groups()) >= 1:
                fields[key] = match.group(len(match.groups())).strip()
            else:
                fields[key] = match.group(1).strip()
        return fields

    def _resolve_patterns(self, template_name: str, form_category: str) -> dict[str, str]:
        if template_name in self.template_patterns:
            return self.template_patterns[template_name]
        if form_category in self.template_patterns:
            return self.template_patterns[form_category]
        return self.generic_patterns
