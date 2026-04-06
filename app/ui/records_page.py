from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
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

        self.page_size = 25
        self.current_page = 1
        self.total_records = 0

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
        refresh.clicked.connect(lambda: self.refresh(reset_page=True))
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

        pager = QHBoxLayout()
        self.prev_btn = QPushButton('Previous')
        self.prev_btn.clicked.connect(self.prev_page)
        self.next_btn = QPushButton('Next')
        self.next_btn.clicked.connect(self.next_page)
        self.page_label = QLabel()
        pager.addWidget(self.prev_btn)
        pager.addWidget(self.next_btn)
        pager.addWidget(self.page_label)
        pager.addStretch()
        layout.addLayout(pager)

        self.records = []
        self.refresh(log_search=False, reset_page=True)

    def clear_filters(self):
        self.category.setCurrentIndex(0)
        self.status.setCurrentIndex(0)
        self.patient_name.clear()
        self.patient_id.clear()
        self.record_number.clear()
        self.refresh(reset_page=True)

    def _filters(self):
        return {
            'category': self.category.currentText(),
            'status': self.status.currentText(),
            'patient_name': self.patient_name.text().strip(),
            'patient_identifier': self.patient_id.text().strip(),
            'record_number': self.record_number.text().strip(),
        }

    def refresh(self, log_search: bool = True, reset_page: bool = False):
        if reset_page:
            self.current_page = 1

        filters = self._filters()
        self.total_records = self.repo.count_records(**filters)
        offset = (self.current_page - 1) * self.page_size
        self.records = self.repo.list_records(**filters, limit=self.page_size, offset=offset)

        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(self.records))
        for row, rec in enumerate(self.records):
            self.table.setItem(row, 0, QTableWidgetItem(str(rec.id)))
            self.table.setItem(row, 1, QTableWidgetItem(rec.record_number))
            self.table.setItem(row, 2, QTableWidgetItem(rec.form_category))
            self.table.setItem(row, 3, QTableWidgetItem(rec.patient_name or ''))
            self.table.setItem(row, 4, QTableWidgetItem(rec.review_status))
        self.table.setSortingEnabled(True)

        total_pages = max(1, (self.total_records + self.page_size - 1) // self.page_size)
        self.page_label.setText(f'Page {self.current_page} / {total_pages} ({self.total_records} records)')
        self.prev_btn.setEnabled(self.current_page > 1)
        self.next_btn.setEnabled(self.current_page < total_pages)

        if log_search:
            self.audit.log(user_id=self.current_user.id, action='record_search', details=str(filters))

    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.refresh(log_search=False)

    def next_page(self):
        total_pages = max(1, (self.total_records + self.page_size - 1) // self.page_size)
        if self.current_page < total_pages:
            self.current_page += 1
            self.refresh(log_search=False)

    def open_selected(self):
        row = self.table.currentRow()
        if row < 0:
            return
        dialog = RecordDetailsDialog(self.session, self.current_user, self.records[row], on_saved=self.refresh)
        dialog.exec()
