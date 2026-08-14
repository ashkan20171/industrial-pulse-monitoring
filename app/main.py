"""
IndustrialPulse Application Entry Point.

Smart Industrial Monitoring & Predictive Maintenance Platform.

Developed by Ashkan Motaei.
Copyright (c) 2026 Ashkan Motaei.
"""

import sys

from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication, QLabel, QMainWindow, QVBoxLayout, QWidget


APP_NAME = "IndustrialPulse"
APP_VERSION = "0.1.0"
DEVELOPER_NAME = "Ashkan Motaei"


class MainWindow(QMainWindow):
    """Main application window for IndustrialPulse."""

    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle(f"{APP_NAME} — Smart Industrial Monitoring")
        self.setMinimumSize(1100, 700)

        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)

        title = QLabel(APP_NAME)
        title.setObjectName("appTitle")

        subtitle = QLabel("Smart Industrial Monitoring & Predictive Maintenance Platform")
        subtitle.setObjectName("appSubtitle")

        developer_label = QLabel(f"Developed by {DEVELOPER_NAME}")
        developer_label.setObjectName("developerLabel")

        layout.addStretch()
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(20)
        layout.addWidget(developer_label)
        layout.addStretch()

        layout.setContentsMargins(60, 60, 60, 60)
        self.setCentralWidget(central_widget)


def apply_dark_theme(application: QApplication) -> None:
    """Apply the initial dark industrial color palette."""

    palette = QPalette()

    palette.setColor(QPalette.ColorRole.Window, QColor("#101828"))
    palette.setColor(QPalette.ColorRole.WindowText, QColor("#F9FAFB"))
    palette.setColor(QPalette.ColorRole.Base, QColor("#1D2939"))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#344054"))
    palette.setColor(QPalette.ColorRole.Text, QColor("#F9FAFB"))
    palette.setColor(QPalette.ColorRole.Button, QColor("#1D2939"))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor("#F9FAFB"))
    palette.setColor(QPalette.ColorRole.Highlight, QColor("#2E90FA"))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#FFFFFF"))

    application.setPalette(palette)

    application.setStyleSheet("""
        QLabel#appTitle {
            color: #F9FAFB;
            font-size: 42px;
            font-weight: 700;
        }

        QLabel#appSubtitle {
            color: #98A2B3;
            font-size: 18px;
        }

        QLabel#developerLabel {
            color: #2E90FA;
            font-size: 15px;
            font-weight: 600;
        }
    """)


def main() -> None:
    """Start the IndustrialPulse application."""

    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    app.setOrganizationName(DEVELOPER_NAME)

    apply_dark_theme(app)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
