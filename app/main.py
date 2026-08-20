"""
IndustrialPulse Application Entry Point.

Smart Industrial Monitoring & Predictive Maintenance Platform.
Developed by Ashkan Motaei.
Copyright (c) 2026 Ashkan Motaei.
"""

import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from app.infrastructure.alerts_manager import AlertsManager
from app.infrastructure.database import init_db
from app.infrastructure.sensor_hub import SensorDataHub
from app.presentation.main_window import MainWindow
from app.presentation.styles.theme import apply_dark_theme

APP_NAME = "IndustrialPulse"
APP_VERSION = "0.3.0"
DEVELOPER_NAME = "Ashkan Motaei"


def main() -> None:
    """Start the IndustrialPulse application."""
    # 1. Initialize SQLite Database & Seed Default Data
    init_db()

    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    app.setOrganizationName(DEVELOPER_NAME)

    # 2. Apply Custom Industrial Dark Theme
    apply_dark_theme(app)

    # 3. Instantiate Shared Core Infrastructure (Singletons)
    alerts_manager = AlertsManager()
    sensor_hub = SensorDataHub()

    # 4. Wire Telemetry Alerts with Queued Connection (Thread-safe DB writing)
    sensor_hub.alert_generated.connect(
        alerts_manager.save_alert_to_db,
        Qt.ConnectionType.QueuedConnection,
    )

    # 5. Inject dependencies into UI Shell
    window = MainWindow(sensor_hub=sensor_hub, alerts_manager=alerts_manager)
    window.show()

    # 6. Start telemetry simulator loop
    sensor_hub.start()

    exit_code = app.exec()

    # 7. Safe Resource Cleanup on Application Exit
    sensor_hub.stop()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
