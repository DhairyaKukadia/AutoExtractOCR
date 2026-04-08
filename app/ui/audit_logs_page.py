from datetime import datetime, time

from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QDateEdit,
    QHBoxLayout,
    QLabel,
    QLineEdit,
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

        filters = QHBoxLayout()
        self.user_id = QLineEdit()
        self.user_id.setPlaceholderText('User ID')
        self.action = QLineEdit()
        self.action.setPlaceholderText('Action')
        self.date_from = QDateEdit(QDate.currentDate().addDays(-7))
        self.date_from.setCalendarPopup(True)
        self.date_to = QDateEdit(QDate.currentDate())
        self.date_to.setCalendarPopup(True)
        apply_btn = QPushButton('Apply Filters')
        apply_btn.clicked.connect(self.refresh)
        filters.addWidget(QLabel('User'))
        filters.addWidget(self.user_id)
        filters.addWidget(QLabel('Action'))
        filters.addWidget(self.action)
        filters.addWidget(QLabel('From'))
        filters.addWidget(self.date_from)
        filters.addWidget(QLabel('To'))
        filters.addWidget(self.date_to)
        filters.addWidget(apply_btn)
        layout.addLayout(filters)

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(['Time', 'User ID', 'Action', 'Status', 'Entity', 'Details'])
        layout.addWidget(self.table)
        self.refresh()

    def refresh(self):
        uid = int(self.user_id.text()) if self.user_id.text().strip().isdigit() else None
        action = self.action.text().strip()
        date_from = datetime.combine(self.date_from.date().toPython(), time.min)
        date_to = datetime.combine(self.date_to.date().toPython(), time.max)
        logs = self.repo.list_recent(300, user_id=uid, action=action, date_from=date_from, date_to=date_to)
        self.table.setRowCount(len(logs))
        for row, log in enumerate(logs):
            self.table.setItem(row, 0, QTableWidgetItem(str(log.timestamp)))
            self.table.setItem(row, 1, QTableWidgetItem(str(log.user_id or '')))
            self.table.setItem(row, 2, QTableWidgetItem(log.action))
            self.table.setItem(row, 3, QTableWidgetItem(log.status))
            self.table.setItem(row, 4, QTableWidgetItem(f'{log.entity_type}:{log.entity_id}'))
            self.table.setItem(row, 5, QTableWidgetItem(log.action_details))
