import json

from PySide6.QtWidgets import QComboBox, QDialog, QFormLayout, QHBoxLayout, QLabel, QLineEdit, QMessageBox, QPushButton, QTextEdit, QVBoxLayout

from app.config.constants import ReviewStatus
from app.services.audit_service import AuditService
from app.services.record_service import RecordService


class RecordDetailsDialog(QDialog):
    def __init__(self, session, current_user, record, on_saved=None):
        super().__init__()
        self.record = record
        self.current_user = current_user
        self.on_saved = on_saved
        self.record_service = RecordService(session)
        self.audit_service = AuditService(session)

        self.setWindowTitle(f'Record {record.record_number}')
        self.resize(900, 600)

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.record_number = QLineEdit(record.record_number)
        self.record_number.setReadOnly(True)
        self.category = QLineEdit(record.form_category)
        self.category.setReadOnly(True)
        self.patient_name = QLineEdit(record.patient_name or '')
        self.patient_identifier = QLineEdit(record.patient_identifier or '')
        self.form_type = QLineEdit(record.form_type or '')
        self.status = QComboBox()
        self.status.addItems([s.value for s in ReviewStatus])
        self.status.setCurrentText(record.review_status)

        form.addRow('Record Number', self.record_number)
        form.addRow('Category', self.category)
        form.addRow('Patient Name', self.patient_name)
        form.addRow('Patient ID', self.patient_identifier)
        form.addRow('Form Type', self.form_type)
        form.addRow('Status', self.status)
        layout.addLayout(form)

        layout.addWidget(QLabel('Raw OCR Text'))
        self.raw = QTextEdit(record.raw_ocr_text)
        layout.addWidget(self.raw)

        actions = QHBoxLayout()
        save_btn = QPushButton('Save Updates')
        save_btn.clicked.connect(self._save_updates)
        close_btn = QPushButton('Close')
        close_btn.clicked.connect(self.close)
        actions.addWidget(save_btn)
        actions.addWidget(close_btn)
        layout.addLayout(actions)

    def _save_updates(self):
        status = self.status.currentText()
        extracted = {
            'patient_name': self.patient_name.text().strip(),
            'patient_identifier': self.patient_identifier.text().strip(),
            'form_type': self.form_type.text().strip(),
        }
        try:
            updated = self.record_service.update_record(
                record_id=self.record.id,
                extracted_fields=extracted,
                raw_ocr_text=self.raw.toPlainText(),
                status=status,
                reviewed_by=self.current_user.id if status in {ReviewStatus.REVIEWED.value, ReviewStatus.APPROVED.value} else None,
            )
        except Exception as exc:
            QMessageBox.critical(self, 'Update failed', str(exc))
            return

        self.record = updated
        action = 'record_update'
        if status == ReviewStatus.REVIEWED.value:
            action = 'record_review'
        elif status == ReviewStatus.APPROVED.value:
            action = 'record_approve'
        elif status == ReviewStatus.REJECTED.value:
            action = 'record_reject'

        self.audit_service.log(
            user_id=self.current_user.id,
            action=action,
            entity_type='medical_record',
            entity_id=str(updated.id),
            details=json.dumps(extracted),
        )
        if self.on_saved:
            self.on_saved()
        QMessageBox.information(self, 'Updated', 'Record updated successfully.')
