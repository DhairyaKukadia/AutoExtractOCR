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

from app.config.constants import Role
from app.services.audit_service import AuditService
from app.services.user_service import UserService


class UsersPage(QWidget):
    def __init__(self, session, current_user):
        super().__init__()
        self.current_user = current_user
        self.service = UserService(session)
        self.audit = AuditService(session)

        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.username = QLineEdit()
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.full_name = QLineEdit()
        self.role = QComboBox()
        self.role.addItems([Role.ADMIN, Role.OPERATOR, Role.REVIEWER])
        form.addRow('Username', self.username)
        form.addRow('Password', self.password)
        form.addRow('Full name', self.full_name)
        form.addRow('Role', self.role)
        layout.addLayout(form)

        actions = QHBoxLayout()
        add_btn = QPushButton('Create User')
        add_btn.clicked.connect(self.create_user)
        deactivate_btn = QPushButton('Deactivate Selected')
        deactivate_btn.clicked.connect(lambda: self._set_selected_active(False))
        activate_btn = QPushButton('Activate Selected')
        activate_btn.clicked.connect(lambda: self._set_selected_active(True))
        actions.addWidget(add_btn)
        actions.addWidget(deactivate_btn)
        actions.addWidget(activate_btn)
        layout.addLayout(actions)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(['ID', 'Username', 'Full Name', 'Role', 'Active'])
        layout.addWidget(self.table)
        self.users = []
        self.refresh()

    def create_user(self):
        try:
            created = self.service.create_user(
                username=self.username.text().strip(),
                password=self.password.text(),
                full_name=self.full_name.text().strip(),
                role=self.role.currentText(),
            )
            self.audit.log(
                user_id=self.current_user.id,
                action='user_create',
                entity_type='user',
                entity_id=str(created.id),
                details=created.username,
            )
            self.username.clear()
            self.password.clear()
            self.full_name.clear()
            self.refresh()
        except Exception as exc:
            QMessageBox.warning(self, 'Error', str(exc))

    def _set_selected_active(self, is_active: bool):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.information(self, 'Select user', 'Please select a user first.')
            return

        target = self.users[row]
        if target.id == self.current_user.id and not is_active:
            QMessageBox.warning(self, 'Invalid action', 'You cannot deactivate your own active session.')
            return

        try:
            updated = self.service.set_user_active(target.id, is_active)
            self.audit.log(
                user_id=self.current_user.id,
                action='user_activate' if is_active else 'user_deactivate',
                entity_type='user',
                entity_id=str(updated.id),
                details=updated.username,
            )
            self.refresh()
        except Exception as exc:
            QMessageBox.warning(self, 'Error', str(exc))

    def refresh(self):
        self.users = self.service.list_users()
        self.table.setRowCount(len(self.users))
        for row, user in enumerate(self.users):
            self.table.setItem(row, 0, QTableWidgetItem(str(user.id)))
            self.table.setItem(row, 1, QTableWidgetItem(user.username))
            self.table.setItem(row, 2, QTableWidgetItem(user.full_name))
            self.table.setItem(row, 3, QTableWidgetItem(user.role))
            self.table.setItem(row, 4, QTableWidgetItem('Yes' if user.is_active else 'No'))
