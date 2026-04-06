from PySide6.QtWidgets import QMainWindow, QTabWidget

from app.config.constants import Role
from app.services.audit_service import AuditService
from app.ui.audit_logs_page import AuditLogsPage
from app.ui.dashboard_page import DashboardPage
from app.ui.ocr_page import OCRPage
from app.ui.records_page import RecordsPage
from app.ui.users_page import UsersPage


class MainWindow(QMainWindow):
    def __init__(self, session, current_user):
        super().__init__()
        self.session = session
        self.current_user = current_user
        self.audit = AuditService(session)
        self.setWindowTitle(f'AutoExtractOCR - {current_user.full_name}')
        tabs = QTabWidget()
        tabs.addTab(DashboardPage(session), 'Dashboard')
        tabs.addTab(OCRPage(session, current_user), 'OCR Intake')
        tabs.addTab(RecordsPage(session, current_user), 'Records')
        if current_user.role == Role.ADMIN:
            tabs.addTab(UsersPage(session, current_user), 'Users')
            tabs.addTab(AuditLogsPage(session), 'Audit Logs')
        self.setCentralWidget(tabs)

    def closeEvent(self, event):
        self.audit.log(user_id=self.current_user.id, action='logout')
        super().closeEvent(event)
