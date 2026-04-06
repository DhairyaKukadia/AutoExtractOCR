from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from app.services.dashboard_service import DashboardService


class DashboardPage(QWidget):
    def __init__(self, session):
        super().__init__()
        self.service = DashboardService(session)
        self.labels = {}
        layout = QVBoxLayout(self)
        for key in ['total_records', 'pending_review', 'approved', 'total_users']:
            lbl = QLabel()
            self.labels[key] = lbl
            layout.addWidget(lbl)
        self.refresh()

    def refresh(self):
        data = self.service.summary()
        self.labels['total_records'].setText(f"Total Records: {data['total_records']}")
        self.labels['pending_review'].setText(f"Pending Review: {data['pending_review']}")
        self.labels['approved'].setText(f"Approved: {data['approved']}")
        self.labels['total_users'].setText(f"Total Users: {data['total_users']}")
