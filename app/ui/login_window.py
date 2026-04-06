from PySide6.QtWidgets import QHBoxLayout, QLabel, QLineEdit, QMessageBox, QPushButton, QVBoxLayout, QWidget

from app.services.audit_service import AuditService
from app.services.auth_service import AuthService


class LoginWindow(QWidget):
    def __init__(self, session, on_login_success):
        super().__init__()
        self.session = session
        self.auth_service = AuthService(session)
        self.audit_service = AuditService(session)
        self.on_login_success = on_login_success
        self.setWindowTitle('AutoExtractOCR - Login')
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        self.username = QLineEdit()
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        login_btn = QPushButton('Login')
        login_btn.clicked.connect(self._login)
        form = QVBoxLayout()
        form.addWidget(QLabel('Username'))
        form.addWidget(self.username)
        form.addWidget(QLabel('Password'))
        form.addWidget(self.password)
        layout.addLayout(form)
        row = QHBoxLayout()
        row.addWidget(login_btn)
        layout.addLayout(row)

    def _login(self):
        username = self.username.text().strip()
        user = self.auth_service.login(username, self.password.text())
        if not user:
            self.audit_service.log(user_id=None, action='login_failure', details=f'username={username}', status='failed')
            QMessageBox.warning(self, 'Login failed', 'Invalid credentials or inactive user')
            return
        self.audit_service.log(user_id=user.id, action='login_success')
        self.on_login_success(user)
        self.close()
