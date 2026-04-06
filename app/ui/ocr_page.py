from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QFileDialog,
    QComboBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.config.constants import FORM_CATEGORIES, OCR_LAYOUT_FIELDS, ReviewStatus
from app.services.audit_service import AuditService
from app.services.ocr_service import OCRService
from app.services.parser_service import ParserService
from app.services.record_service import RecordService
from app.utils.file_utils import is_supported_file


class OCRPage(QWidget):
    def __init__(self, session, current_user):
        super().__init__()
        self.session = session
        self.current_user = current_user
        self.ocr_service = OCRService()
        self.parser_service = ParserService()
        self.record_service = RecordService(session)
        self.audit_service = AuditService(session)
        self.file_path = ''
        self.has_ocr_result = False
        self.field_inputs: dict[str, QLineEdit] = {}
        self._build_ui()
        self._configure_shortcuts()
        self._load_fields_for_category(self.category.currentText())
        self._update_save_enabled()

    def _build_ui(self):
        root = QVBoxLayout(self)

        controls = QHBoxLayout()
        self.file_label = QLabel('No file selected')
        browse = QPushButton('Upload File')
        browse.clicked.connect(self._select_file)

        self.category = QComboBox()
        self.category.addItems(FORM_CATEGORIES)
        self.category.currentTextChanged.connect(self._on_category_changed)

        self.status = QComboBox()
        self.status.addItems([s.value for s in ReviewStatus])
        self.status.setCurrentText(ReviewStatus.DRAFT.value)

        run_btn = QPushButton('Run OCR')
        run_btn.clicked.connect(self._run_ocr)

        self.save_btn = QPushButton('Save Record')
        self.save_btn.clicked.connect(self._save)

        controls.addWidget(self.file_label, 1)
        controls.addWidget(QLabel('Category'))
        controls.addWidget(self.category)
        controls.addWidget(QLabel('Status'))
        controls.addWidget(self.status)
        controls.addWidget(browse)
        controls.addWidget(run_btn)
        controls.addWidget(self.save_btn)
        root.addLayout(controls)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        self.raw_text = QTextEdit()
        self.raw_text.setPlaceholderText('Raw OCR text')
        self.raw_text.setReadOnly(True)
        splitter.addWidget(self.raw_text)

        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.addWidget(QLabel('Structured Fields'))
        self.form_layout = QFormLayout()
        for key in OCR_LAYOUT_FIELDS:
            line = QLineEdit()
            self.field_inputs[key] = line
            self.form_layout.addRow(key.replace('_', ' ').title(), line)

    def _select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, 'Select form', '', 'Documents (*.png *.jpg *.jpeg *.pdf)')
        if not file_path:
            return
        if not is_supported_file(file_path):
            QMessageBox.warning(self, 'Invalid file', 'Supported: PNG, JPG, JPEG, PDF')
            return

        self.file_path = file_path
        self.file_label.setText(Path(file_path).name)
        self.has_ocr_result = False
        self.raw_text.clear()
        for widget in self.field_inputs.values():
            widget.clear()

        self.audit_service.log(user_id=self.current_user.id, action='file_upload', details=file_path)
        self._update_save_enabled()

    def _run_ocr(self):
        if not self.file_path:
            QMessageBox.warning(self, 'Missing file', 'Please upload a file first.')
            return

        try:
            text, _confidence = self.ocr_service.run(self.file_path)
        except Exception as exc:
            QMessageBox.critical(self, 'OCR failure', str(exc))
            self.audit_service.log(user_id=self.current_user.id, action='ocr_execution', details=str(exc), status='failed')
            return

        self.has_ocr_result = True
        self.raw_text.setText(text)
        for key, value in self.extraction_service.parse(text, template_name=self.category.currentText()).items():
            self.field_inputs[key].setText(value)
        self.status.setCurrentText(ReviewStatus.EXTRACTED.value)
        self.has_ocr_result = True
        self.audit_service.log(user_id=self.current_user.id, action='ocr_execution', details=self.file_path)
        self._update_save_enabled()

    def _update_save_enabled(self):
        self.save_btn.setEnabled(bool(self.file_path and self.has_ocr_result))

    def _save(self):
        if not self.save_btn.isEnabled():
            QMessageBox.warning(self, 'Cannot save', 'Save is enabled only after file upload and OCR execution.')
            return

        category = self.category.currentText()
        target_table = FORM_CATEGORY_TO_TABLE.get(category)
        if not target_table:
            QMessageBox.critical(self, 'Invalid category', 'Selected category has no database mapping.')
            return

        extracted = {key: widget.text().strip() for key, widget in self.field_inputs.items()}
        extracted['__target_table'] = target_table
        extracted['__category'] = category

        record = self.record_service.save_record(
            form_category=category,
            source_file_name=Path(self.file_path).name,
            source_file_path=self.file_path,
            raw_ocr_text=self.raw_text.toPlainText(),
            extracted_fields=extracted,
            status=ReviewStatus.EXTRACTED.value,
            created_by=self.current_user.id,
        )
        self.audit_service.log(
            user_id=self.current_user.id,
            action='record_save',
            entity_type='medical_record',
            entity_id=str(record.id),
            details=f'{record.record_number} -> {target_table}',
        )
        QMessageBox.information(self, 'Saved', f'Record saved: {record.record_number}')
