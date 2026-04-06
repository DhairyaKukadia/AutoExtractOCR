import json

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QComboBox, QDialog, QFormLayout, QHBoxLayout, QLineEdit, QMessageBox, QPushButton, QTextEdit, QVBoxLayout

from app.config.constants import Role, ReviewStatus
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

        self.record_no = QLineEdit(record.record_number)
        self.record_no.setReadOnly(True)
        self.category = QLineEdit(record.form_category)
        self.category.setReadOnly(True)
        self.patient_name = QLineEdit(record.patient_name or '')
        self.patient_name.setReadOnly(True)

        self.status = QComboBox()
        self.status.addItems([s.value for s in ReviewStatus])
        self.status.setCurrentText(record.review_status)
        self._enforce_role_status_rules()

        for label, widget in [
            ('Record Number', self.record_no),
            ('Category', self.category),
            ('Patient', self.patient_name),
            ('Status', self.status),
        ]:
            widget.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            form.addRow(label, widget)
        layout.addLayout(form)

        self.structured = QTextEdit(self._pretty_json(record.extracted_json))
        layout.addWidget(self.structured)

        self.raw = QTextEdit(record.raw_ocr_text)
        self.raw.setReadOnly(True)
        layout.addWidget(self.raw)

        actions = QHBoxLayout()
        save_btn = QPushButton('Update Status')
        save_btn.clicked.connect(self._save_status)
        actions.addWidget(save_btn)
        layout.addLayout(actions)

    def _enforce_role_status_rules(self):
        if self.current_user.role in {Role.ADMIN, Role.REVIEWER}:
            return
        for value in [ReviewStatus.REVIEWED.value, ReviewStatus.APPROVED.value, ReviewStatus.REJECTED.value]:
            idx = self.status.findText(value)
            if idx >= 0:
                self.status.model().item(idx).setEnabled(False)

    def _save_status(self):
        new_status = self.status.currentText()
        if self.current_user.role not in {Role.ADMIN, Role.REVIEWER} and new_status in {
            ReviewStatus.REVIEWED.value,
            ReviewStatus.APPROVED.value,
            ReviewStatus.REJECTED.value,
        }:
            QMessageBox.warning(self, 'Permission denied', 'Only Reviewer/Admin can set reviewed/approved/rejected.')
            return

        old_status = self.record.review_status
        self.record = self.record_service.update_record_status(self.record.id, new_status, reviewed_by=self.current_user.id)
        self.audit_service.log(
            user_id=self.current_user.id,
            action='status_update',
            entity_type='medical_record',
            entity_id=str(self.record.id),
            details=f'{old_status} -> {new_status} ({self.record.record_number})',
        )
        QMessageBox.information(self, 'Updated', 'Status updated successfully.')
        if self.on_saved:
            self.on_saved()

    @staticmethod
    def _pretty_json(payload: str) -> str:
        try:
            return json.dumps(json.loads(payload or '{}'), indent=2)
        except Exception:
            return payload or ''
