from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QFormLayout, QLineEdit, QTextEdit, QVBoxLayout


class RecordDetailsDialog(QDialog):
    def __init__(self, record):
        super().__init__()
        self.setWindowTitle(f'Record {record.record_number}')
        self.resize(800, 500)

        layout = QVBoxLayout(self)
        form = QFormLayout()

        for label, value in [
            ('Record Number', record.record_number),
            ('Category', record.form_category),
            ('Patient Name', record.patient_name or ''),
            ('Patient ID', record.patient_identifier or ''),
            ('Status', record.review_status),
        ]:
            field = QLineEdit(value)
            field.setReadOnly(True)
            field.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            form.addRow(label, field)

        layout.addLayout(form)

        raw = QTextEdit(record.raw_ocr_text)
        raw.setReadOnly(True)
        layout.addWidget(raw)
