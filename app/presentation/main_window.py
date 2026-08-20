"""
Main window shell for IndustrialPulse.
Developed by Ashkan Motaei.
"""

from __future__ import annotations

from PySide6.QtWidgets import (
    QButtonGroup,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from app.infrastructure.alerts_manager import AlertsManager
from app.infrastructure.sensor_hub import SensorDataHub
from app.presentation.pages.alerts_page import AlertsPage
from app.presentation.pages.dashboard_page import DashboardPage
from app.presentation.pages.equipment_page import EquipmentPage
from app.presentation.pages.monitoring_page import MonitoringPage
from app.presentation.pages.work_orders_page import WorkOrdersPage


class PlaceholderPage(QWidget):
    """Temporary placeholder page for sections under development."""

    def __init__(self, title: str, description: str) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)

        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 28px; font-weight: 700; color: #F9FAFB;")

        description_label = QLabel(description)
        description_label.setStyleSheet("font-size: 14px; color: #98A2B3;")
        description_label.setWordWrap(True)

        developer_label = QLabel("Developed by Ashkan Motaei")
        developer_label.setObjectName("developerBadge")

        layout.addStretch()
        layout.addWidget(title_label)
        layout.addWidget(description_label)
        layout.addSpacing(12)
        layout.addWidget(developer_label)
        layout.addStretch()


class MainWindow(QMainWindow):
    """Primary application shell, orchestrates pages and background services."""

    def __init__(
        self, sensor_hub: SensorDataHub, alerts_manager: AlertsManager
    ) -> None:
        super().__init__()

        self.sensor_hub = sensor_hub
        self.alerts_manager = alerts_manager

        self.setWindowTitle("IndustrialPulse - Developed by Ashkan Motaei")
        self.setMinimumSize(1360, 840)

        # Page index mapping for titles and descriptions
        self.page_titles = {
            0: (
                "Industrial Dashboard",
                "Real-time monitoring and maintenance intelligence",
            ),
            1: (
                "Equipment",
                "Asset registry, operational state, and equipment metadata",
            ),
            2: (
                "Monitoring",
                "Live sensor streams and process visibility",
            ),
            3: (
                "Alerts Center",
                "Review and manage active system alerts",
            ),
            4: (
                "Work Orders",
                "Schedule, track, and manage maintenance tasks",
            ),
        }

        # Initialize pages with shared managers
        self.dashboard_page = DashboardPage(sensor_hub=self.sensor_hub)
        self.equipment_page = EquipmentPage()
        self.monitoring_page = MonitoringPage(sensor_hub=self.sensor_hub)
        self.alerts_page = AlertsPage(alerts_manager=self.alerts_manager)
        self.work_orders_page = WorkOrdersPage()

        # Stack configuration
        self.stack = QStackedWidget()
        self.stack.addWidget(self.dashboard_page)    # Index 0
        self.stack.addWidget(self.equipment_page)     # Index 1
        self.stack.addWidget(self.monitoring_page)    # Index 2
        self.stack.addWidget(self.alerts_page)        # Index 3
        self.stack.addWidget(self.work_orders_page)   # Index 4

        # Header widgets
        self.page_title_label = QLabel()
        self.page_title_label.setObjectName("pageTitle")
        self.page_subtitle_label = QLabel()
        self.page_subtitle_label.setObjectName("pageSubtitle")

        # Root layout
        central_widget = QWidget()
        root_layout = QHBoxLayout(central_widget)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        root_layout.addWidget(self._build_sidebar(), 0)
        root_layout.addWidget(self._build_content_area(), 1)

        self.setCentralWidget(central_widget)
        self._set_active_page(0)

    def _build_sidebar(self) -> QFrame:
        """Builds the navigation sidebar."""
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(250)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(18, 20, 18, 20)
        layout.setSpacing(12)

        brand_title = QLabel("IndustrialPulse")
        brand_title.setObjectName("brandTitle")
        brand_subtitle = QLabel("Developed by Ashkan Motaei")
        brand_subtitle.setObjectName("brandSubtitle")

        layout.addWidget(brand_title)
        layout.addWidget(brand_subtitle)
        layout.addSpacing(20)

        self.nav_group = QButtonGroup(self)
        self.nav_group.setExclusive(True)

        nav_items = [
            "Dashboard",
            "Equipment",
            "Monitoring",
            "Alerts Center",
            "Work Orders",
        ]

        for index, text in enumerate(nav_items):
            button = QPushButton(text)
            button.setObjectName("navButton")
            button.setCheckable(True)
            button.clicked.connect(
                lambda checked=False, page_index=index: self._set_active_page(page_index)
            )
            self.nav_group.addButton(button, index)
            layout.addWidget(button)

        layout.addStretch()

        footer = QLabel("Industrial software portfolio by Ashkan Motaei")
        footer.setStyleSheet("color: #667085; font-size: 11px;")
        footer.setWordWrap(True)
        layout.addWidget(footer)

        return sidebar

    def _build_content_area(self) -> QWidget:
        """Builds the main content shell."""
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(24, 20, 24, 24)
        layout.setSpacing(20)

        top_bar = QFrame()
        top_bar.setObjectName("topBar")
        top_layout = QVBoxLayout(top_bar)
        top_layout.setContentsMargins(0, 0, 0, 16)
        top_layout.setSpacing(4)
        top_layout.addWidget(self.page_title_label)
        top_layout.addWidget(self.page_subtitle_label)

        layout.addWidget(top_bar)
        layout.addWidget(self.stack, 1)

        return content

    def _set_active_page(self, index: int) -> None:
        """Switches current stack view and updates navigation UI."""
        self.stack.setCurrentIndex(index)

        button = self.nav_group.button(index)
        if button:
            button.setChecked(True)

        title, subtitle = self.page_titles.get(index, ("Unknown Page", ""))
        self.page_title_label.setText(title)
        self.page_subtitle_label.setText(subtitle)

    def closeEvent(self, event) -> None:
        """Clean shutdown of all child timers and background threads."""
        try:
            for page in (
                self.dashboard_page,
                self.monitoring_page,
                self.alerts_page,
                self.work_orders_page,
            ):
                shutdown_fn = getattr(page, "shutdown", None)
                if callable(shutdown_fn):
                    shutdown_fn()

            if self.sensor_hub:
                self.sensor_hub.stop()

        finally:
            event.accept()
