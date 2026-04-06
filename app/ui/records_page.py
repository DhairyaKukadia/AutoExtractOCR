from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.config.constants import FORM_CATEGORIES, ReviewStatus
from app.data.repositories.record_repository import RecordRepository
from app.services.audit_service import AuditService
from app.ui.record_details_dialog import RecordDetailsDialog


class RecordsPage(QWidget):
    def __init__(self, session, current_user):
        super().__init__()
        self.current_user = current_user
        self.repo = RecordRepository(session)
        self.audit = AuditService(session)
        layout = QVBoxLayout(self)

        filters_form = QFormLayout()
        self.category = QComboBox()
        self.category.addItem('')
        self.category.addItems(FORM_CATEGORIES)
        self.status = QComboBox()
        self.status.addItem('')
        self.status.addItems([s.value for s in ReviewStatus])
        self.patient_name = QLineEdit()
        self.patient_id = QLineEdit()
        self.record_number = QLineEdit()
        filters_form.addRow('Category', self.category)
        filters_form.addRow('Status', self.status)
        filters_form.addRow('Patient Name', self.patient_name)
        filters_form.addRow('Patient Identifier', self.patient_id)
        filters_form.addRow('Record Number', self.record_number)
        layout.addLayout(filters_form)

        actions = QHBoxLayout()
        refresh = QPushButton('Search')
        refresh.clicked.connect(self.refresh)
        clear_btn = QPushButton('Clear')
        clear_btn.clicked.connect(self.clear_filters)
        actions.addWidget(refresh)
        actions.addWidget(clear_btn)
        layout.addLayout(actions)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(['ID', 'Record #', 'Category', 'Patient', 'Status'])
        self.table.setSortingEnabled(True)
        self.table.doubleClicked.connect(self.open_selected)
        layout.addWidget(self.table)

        self.records = []
        self.refresh(log_search=False)

    def clear_filters(self):
        self.category.setCurrentIndex(0)
        self.status.setCurrentIndex(0)
        self.patient_name.clear()
        self.patient_id.clear()
        self.record_number.clear()
        self.refresh()

    def refresh(self, log_search: bool = True):
        filters = {
            'category': self.category.currentText(),
            'status': self.status.currentText(),
            'patient_name': self.patient_name.text().strip(),
            'patient_identifier': self.patient_id.text().strip(),
            'record_number': self.record_number.text().strip(),
        }
        self.records = self.repo.list_records(**filters)
        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(self.records))
        for row, rec in enumerate(self.records):
            self.table.setItem(row, 0, QTableWidgetItem(str(rec.id)))
            self.table.setItem(row, 1, QTableWidgetItem(rec.record_number))
            self.table.setItem(row, 2, QTableWidgetItem(rec.form_category))
            self.table.setItem(row, 3, QTableWidgetItem(rec.patient_name or ''))
            self.table.setItem(row, 4, QTableWidgetItem(rec.review_status))
        self.table.setSortingEnabled(True)
        if log_search:
            self.audit.log(user_id=self.current_user.id, action='record_search', details=str(filters))

    def open_selected(self):
        row = self.table.currentRow()
        if row < 0:
            return
        dialog = RecordDetailsDialog(self.records[row])
        dialog.exec()
