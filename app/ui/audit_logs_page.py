from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget

from app.data.repositories.audit_repository import AuditRepository


class AuditLogsPage(QWidget):
    def __init__(self, session):
        super().__init__()
        self.repo = AuditRepository(session)
        layout = QVBoxLayout(self)
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(['Time', 'User ID', 'Action', 'Status', 'Entity', 'Details'])
        layout.addWidget(self.table)
        self.refresh()

    def refresh(self):
        logs = self.repo.list_recent(300)
        self.table.setRowCount(len(logs))
        for row, log in enumerate(logs):
            self.table.setItem(row, 0, QTableWidgetItem(str(log.timestamp)))
            self.table.setItem(row, 1, QTableWidgetItem(str(log.user_id or '')))
            self.table.setItem(row, 2, QTableWidgetItem(log.action))
            self.table.setItem(row, 3, QTableWidgetItem(log.status))
            self.table.setItem(row, 4, QTableWidgetItem(f'{log.entity_type}:{log.entity_id}'))
            self.table.setItem(row, 5, QTableWidgetItem(log.action_details))
