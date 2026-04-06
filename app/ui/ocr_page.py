from pathlib import Path

from PySide6.QtWidgets import (
    QFileDialog,
    QComboBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.config.constants import FORM_CATEGORIES, OCR_LAYOUT_FIELDS, ReviewStatus
from app.services.audit_service import AuditService
from app.services.extraction_service import ExtractionService
from app.services.ocr_service import OCRService
from app.services.record_service import RecordService
from app.utils.file_utils import is_supported_file


class OCRPage(QWidget):
    def __init__(self, session, current_user):
        super().__init__()
        self.session = session
        self.current_user = current_user
        self.ocr_service = OCRService()
        self.extraction_service = ExtractionService()
        self.record_service = RecordService(session)
        self.audit_service = AuditService(session)
        self.file_path = ''
        self.has_ocr_result = False
        self.field_inputs: dict[str, QLineEdit] = {}
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        top = QHBoxLayout()
        self.file_label = QLabel('No file selected')
        browse = QPushButton('Select File')
        browse.clicked.connect(self._select_file)
        self.category = QComboBox()
        self.category.addItems(FORM_CATEGORIES)
        self.status = QComboBox()
        self.status.addItems([s.value for s in ReviewStatus])
        run_btn = QPushButton('Run OCR')
        run_btn.clicked.connect(self._run_ocr)
        save_btn = QPushButton('Save Record')
        save_btn.clicked.connect(self._save)
        top.addWidget(self.file_label)
        top.addWidget(browse)
        top.addWidget(QLabel('Category'))
        top.addWidget(self.category)
        top.addWidget(QLabel('Status'))
        top.addWidget(self.status)
        top.addWidget(run_btn)
        top.addWidget(save_btn)
        root.addLayout(top)

        self.raw_text = QTextEdit()
        self.raw_text.setPlaceholderText('Raw OCR text')
        root.addWidget(self.raw_text)

        self.form_layout = QFormLayout()
        for key in OCR_LAYOUT_FIELDS:
            line = QLineEdit()
            self.field_inputs[key] = line
            self.form_layout.addRow(key.replace('_', ' ').title(), line)
        root.addLayout(self.form_layout)

    def _select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, 'Select form', '', 'Documents (*.png *.jpg *.jpeg *.pdf)')
        if file_path:
            if not is_supported_file(file_path):
                QMessageBox.warning(self, 'Invalid file', 'Supported: PNG, JPG, JPEG, PDF')
                return
            self.file_path = file_path
            self.has_ocr_result = False
            self.file_label.setText(Path(file_path).name)
            self.raw_text.clear()
            for widget in self.field_inputs.values():
                widget.clear()
            self.audit_service.log(user_id=self.current_user.id, action='file_upload', details=file_path)

    def _run_ocr(self):
        if not self.file_path:
            QMessageBox.warning(self, 'Missing file', 'Please select a file first')
            return
        try:
            text, _confidence = self.ocr_service.run(self.file_path)
        except Exception as exc:
            QMessageBox.critical(self, 'OCR failed', str(exc))
            self.audit_service.log(user_id=self.current_user.id, action='ocr_execution', details=str(exc), status='failed')
            return

        self.has_ocr_result = True
        self.raw_text.setText(text)
        for key, value in self.extraction_service.parse(text, template_name=self.category.currentText()).items():
            self.field_inputs[key].setText(value)
        self.status.setCurrentText(ReviewStatus.EXTRACTED.value)
        self.audit_service.log(user_id=self.current_user.id, action='ocr_execution', details=self.file_path)

    def _save(self):
        if not self.file_path:
            QMessageBox.warning(self, 'Missing file', 'Please select and process a file first')
            return
        if not self.has_ocr_result and not self.raw_text.toPlainText().strip():
            QMessageBox.warning(self, 'Missing OCR', 'Run OCR (or provide raw text) before saving.')
            return

        status = self.status.currentText()
        extracted = {key: widget.text().strip() for key, widget in self.field_inputs.items()}
        record = self.record_service.save_record(
            form_category=self.category.currentText(),
            source_file_name=Path(self.file_path).name,
            source_file_path=self.file_path,
            raw_ocr_text=self.raw_text.toPlainText(),
            extracted_fields=extracted,
            status=status,
            created_by=self.current_user.id,
        )
        self.audit_service.log(
            user_id=self.current_user.id,
            action='record_save',
            entity_type='medical_record',
            entity_id=str(record.id),
            details=record.record_number,
        )
        QMessageBox.information(self, 'Saved', f'Record saved: {record.record_number}')
