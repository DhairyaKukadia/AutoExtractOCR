from datetime import datetime

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
        self.session = session
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
        self.form_type = QLineEdit()
        self.date_from = QLineEdit()
        self.date_from.setPlaceholderText('YYYY-MM-DD')
        self.date_to = QLineEdit()
        self.date_to.setPlaceholderText('YYYY-MM-DD')
        self.record_number = QLineEdit()
        filters_form.addRow('Category', self.category)
        filters_form.addRow('Status', self.status)
        filters_form.addRow('Patient Name', self.patient_name)
        filters_form.addRow('Patient Identifier', self.patient_id)
        filters_form.addRow('Form Type', self.form_type)
        filters_form.addRow('Date From', self.date_from)
        filters_form.addRow('Date To', self.date_to)
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
        self.form_type.clear()
        self.date_from.clear()
        self.date_to.clear()
        self.record_number.clear()
        self.refresh()

    def refresh(self, log_search: bool = True):
        filters = {
            'category': self.category.currentText(),
            'status': self.status.currentText(),
            'patient_name': self.patient_name.text().strip(),
            'patient_identifier': self.patient_id.text().strip(),
            'form_type': self.form_type.text().strip(),
            'date_from': self._parse_date(self.date_from.text().strip(), end_of_day=False),
            'date_to': self._parse_date(self.date_to.text().strip(), end_of_day=True),
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

    @staticmethod
    def _parse_date(raw: str, *, end_of_day: bool) -> datetime | None:
        if not raw:
            return None
        try:
            parsed = datetime.strptime(raw, '%Y-%m-%d')
            return parsed.replace(hour=23, minute=59, second=59) if end_of_day else parsed
        except ValueError:
            return None

    def open_selected(self):
        row = self.table.currentRow()
        if row < 0:
            return
        dialog = RecordDetailsDialog(
            session=self.session,
            current_user=self.current_user,
            record=self.records[row],
            on_saved=self.refresh,
        )
        dialog.exec()
