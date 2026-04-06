import sys

from PySide6.QtWidgets import QApplication

from app.data.database import SessionLocal, init_db, session_scope
from app.data.migrations import ensure_schema_version
from app.data.seed import seed_data
from app.ui.login_window import LoginWindow
from app.ui.main_window import MainWindow
from app.utils.logger import configure_logging


def run() -> None:
    configure_logging()
    init_db()

    with session_scope() as setup_session:
        seed_data(setup_session)
        ensure_schema_version(setup_session)

    app_session = SessionLocal()
    app = QApplication(sys.argv)
    windows = {}

    def on_login_success(user):
        main_window = MainWindow(app_session, user)
        main_window.resize(1200, 700)
        main_window.show()
        windows['main'] = main_window

    login = LoginWindow(app_session, on_login_success)
    login.resize(350, 180)
    login.show()
    windows['login'] = login
    exit_code = app.exec()
    app_session.close()
    sys.exit(exit_code)
