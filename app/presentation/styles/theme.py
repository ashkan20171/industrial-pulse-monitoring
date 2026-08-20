"""Application theme configuration for IndustrialPulse."""

from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication


"""
Dark industrial theme for IndustrialPulse.

Developed by Ashkan Motaei.
"""

from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication


def apply_dark_theme(application: QApplication) -> None:
    """Apply the main dark industrial theme."""

    palette = QPalette()

    palette.setColor(QPalette.ColorRole.Window, QColor("#0F172A"))
    palette.setColor(QPalette.ColorRole.WindowText, QColor("#F8FAFC"))
    palette.setColor(QPalette.ColorRole.Base, QColor("#111827"))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#1E293B"))
    palette.setColor(QPalette.ColorRole.Text, QColor("#F8FAFC"))
    palette.setColor(QPalette.ColorRole.Button, QColor("#1E293B"))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor("#F8FAFC"))
    palette.setColor(QPalette.ColorRole.Highlight, QColor("#3B82F6"))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#FFFFFF"))

    application.setPalette(palette)

    application.setStyleSheet("""
        /* ---------------------------------------------------------
           Global styles
        --------------------------------------------------------- */

        QMainWindow {
            background-color: #0F172A;
        }

        QWidget {
            color: #F8FAFC;
            font-family: "Segoe UI";
            font-size: 14px;
        }

        QLabel {
            background-color: transparent;
            border: none;
        }

        QToolTip {
            color: #F8FAFC;
            background-color: #1E293B;
            border: 1px solid #334155;
            padding: 6px;
        }

        /* ---------------------------------------------------------
           Sidebar
        --------------------------------------------------------- */

        QFrame#sidebar {
            background-color: #0B1220;
            border: none;
            border-right: 1px solid #1E293B;
        }

        QLabel#brandTitle {
            background-color: transparent;
            color: #F8FAFC;
            font-size: 22px;
            font-weight: 700;
        }

        QLabel#brandSubtitle {
            background-color: transparent;
            color: #94A3B8;
            font-size: 11px;
        }

        QPushButton#navButton {
            min-height: 28px;
            background-color: transparent;
            color: #94A3B8;
            border: none;
            border-radius: 8px;
            padding: 11px 14px;
            text-align: left;
            font-size: 14px;
        }

        QPushButton#navButton:hover {
            background-color: #172033;
            color: #F8FAFC;
        }

        QPushButton#navButton:checked {
            background-color: #263753;
            color: #FFFFFF;
            border: 1px solid #3B4D6B;
            font-weight: 600;
        }

        /* ---------------------------------------------------------
           Header
        --------------------------------------------------------- */

        QFrame#topBar {
            background-color: transparent;
            border: none;
            border-bottom: 1px solid #1E293B;
        }

        QLabel#pageTitle {
            background-color: transparent;
            color: #F8FAFC;
            font-size: 24px;
            font-weight: 700;
        }

        QLabel#pageSubtitle {
            background-color: transparent;
            color: #94A3B8;
            font-size: 13px;
        }

        /* ---------------------------------------------------------
           Dashboard cards
        --------------------------------------------------------- */

        QFrame#panelCard {
            background-color: #1E293B;
            border: 1px solid #334155;
            border-radius: 10px;
        }

        QFrame#panelCard:hover {
            border: 1px solid #475569;
            background-color: #202D41;
        }

        QLabel#cardTitle {
            background-color: transparent;
            color: #94A3B8;
            font-size: 12px;
        }

        QLabel#cardValue {
            background-color: transparent;
            color: #F8FAFC;
            font-size: 28px;
            font-weight: 700;
        }

        QLabel#cardHint {
            background-color: transparent;
            color: #3B82F6;
            font-size: 12px;
        }

        /* ---------------------------------------------------------
           Content panels
        --------------------------------------------------------- */

        QFrame#tableLikePanel {
            background-color: #1E293B;
            border: 1px solid #334155;
            border-radius: 10px;
        }

        QLabel#sectionTitle {
            background-color: transparent;
            color: #F8FAFC;
            font-size: 16px;
            font-weight: 600;
        }

        QLabel#developerBadge {
            background-color: transparent;
            color: #3B82F6;
            font-size: 12px;
            font-weight: 600;
        }
    """)
