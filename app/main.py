import sys

from PySide6.QtWidgets import QApplication

from app.data.database import SessionLocal, init_db
from app.data.seed import seed_data
from app.ui.login_window import LoginWindow
from app.ui.main_window import MainWindow
from app.utils.logger import configure_logging


def run() -> None:
    configure_logging()
    init_db()
    session = SessionLocal()
    seed_data(session)

    app = QApplication(sys.argv)
    windows = {}

    def on_login_success(user):
        main_window = MainWindow(session, user)
        main_window.resize(1200, 700)
        main_window.show()
        windows['main'] = main_window

    login = LoginWindow(session, on_login_success)
    login.resize(350, 180)
    login.show()
    windows['login'] = login
    sys.exit(app.exec())
