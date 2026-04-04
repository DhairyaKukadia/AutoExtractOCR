import re


class ExtractionService:
    patterns = {
        'patient_name': r'Patient\s*Name[:\-]?\s*(.+)',
        'patient_identifier': r'(Patient\s*(ID|Identifier)|MRN)[:\-]?\s*([A-Za-z0-9\-]+)',
        'form_type': r'Form\s*Type[:\-]?\s*(.+)',
    }

    def parse(self, text: str) -> dict[str, str]:
        fields: dict[str, str] = {}
        for key, pattern in self.patterns.items():
            match = re.search(pattern, text, flags=re.IGNORECASE)
            if not match:
                fields[key] = ''
            elif key == 'patient_identifier':
                fields[key] = match.group(3).strip()
            else:
                fields[key] = match.group(1).strip()
        return fields
