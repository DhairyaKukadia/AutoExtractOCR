from datetime import datetime

from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.data.repositories.audit_repository import AuditRepository


class AuditLogsPage(QWidget):
    def __init__(self, session):
        super().__init__()
        self.repo = AuditRepository(session)
        layout = QVBoxLayout(self)

        filters = QFormLayout()
        self.user_id = QLineEdit()
        self.action = QLineEdit()
        self.status = QComboBox()
        self.status.addItem('')
        self.status.addItems(['success', 'failed'])
        self.date_from = QLineEdit()
        self.date_from.setPlaceholderText('YYYY-MM-DD')
        self.date_to = QLineEdit()
        self.date_to.setPlaceholderText('YYYY-MM-DD')
        filters.addRow('User ID', self.user_id)
        filters.addRow('Action', self.action)
        filters.addRow('Status', self.status)
        filters.addRow('Date From', self.date_from)
        filters.addRow('Date To', self.date_to)
        layout.addLayout(filters)

        actions = QHBoxLayout()
        apply_btn = QPushButton('Apply Filters')
        apply_btn.clicked.connect(self.refresh)
        clear_btn = QPushButton('Clear')
        clear_btn.clicked.connect(self._clear)
        actions.addWidget(apply_btn)
        actions.addWidget(clear_btn)
        layout.addLayout(actions)

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(['Time', 'User ID', 'Action', 'Status', 'Entity', 'Details'])
        layout.addWidget(self.table)
        self.refresh()

    def _clear(self):
        self.user_id.clear()
        self.action.clear()
        self.status.setCurrentIndex(0)
        self.date_from.clear()
        self.date_to.clear()
        self.refresh()

    def refresh(self):
        user_id = int(self.user_id.text()) if self.user_id.text().strip().isdigit() else None
        date_from_raw = self.date_from.text().strip()
        date_to_raw = self.date_to.text().strip()
        date_from = self._parse_date(date_from_raw, is_end=False)
        date_to = self._parse_date(date_to_raw, is_end=True)

        invalid_fields: list[str] = []
        if date_from_raw and date_from is None:
            invalid_fields.append('Date From')
        if date_to_raw and date_to is None:
            invalid_fields.append('Date To')
        if invalid_fields:
            QMessageBox.warning(self, 'Invalid date', f'Invalid date format for: {", ".join(invalid_fields)}. Use YYYY-MM-DD.')
            return

        logs = self.repo.list_filtered(
            user_id=user_id,
            action=self.action.text().strip(),
            status=self.status.currentText().strip(),
            date_from=date_from,
            date_to=date_to,
            limit=500,
        )
        self.table.setRowCount(len(logs))
        for row, log in enumerate(logs):
            self.table.setItem(row, 0, QTableWidgetItem(str(log.timestamp)))
            self.table.setItem(row, 1, QTableWidgetItem(str(log.user_id or '')))
            self.table.setItem(row, 2, QTableWidgetItem(log.action))
            self.table.setItem(row, 3, QTableWidgetItem(log.status))
            self.table.setItem(row, 4, QTableWidgetItem(f'{log.entity_type}:{log.entity_id}'))
            self.table.setItem(row, 5, QTableWidgetItem(log.action_details))

    @staticmethod
    def _parse_date(raw: str, *, is_end: bool) -> datetime | None:
        if not raw:
            return None
        try:
            base = datetime.strptime(raw, '%Y-%m-%d')
            if is_end:
                return base.replace(hour=23, minute=59, second=59)
            return base
        except ValueError:
            return None
