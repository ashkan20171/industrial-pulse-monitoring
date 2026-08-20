"""
Dashboard page for IndustrialPulse.
Developed by Ashkan Motaei.
"""

from __future__ import annotations

from PySide6.QtCore import Qt, Slot, QThread
from PySide6.QtWidgets import QFrame, QGridLayout, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from app.infrastructure.sensor_hub import SensorDataHub, SensorReadout


class StatCard(QFrame):
    """Small KPI card used on the dashboard."""

    def __init__(self, title: str, value: str, hint: str) -> None:
        super().__init__()
        self.setObjectName("panelCard")
        self.setMinimumHeight(135)
        self.setMaximumHeight(150)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(8)

        self.title_label = QLabel(title)
        self.title_label.setObjectName("cardTitle")

        self.value_label = QLabel(value)
        self.value_label.setObjectName("cardValue")

        self.hint_label = QLabel(hint)
        self.hint_label.setObjectName("cardHint")

        layout.addWidget(self.title_label)
        layout.addWidget(self.value_label)
        layout.addStretch()
        layout.addWidget(self.hint_label)


class DashboardPage(QWidget):
    """Main dashboard view with live updates from Sensor Hub."""

    def __init__(self, sensor_hub: SensorDataHub) -> None:
        super().__init__()
        self.sensor_hub = sensor_hub

        self._setup_ui()

        # Connect to the central sensor hub
        self.sensor_hub.data_available.connect(self._update_live_data)

    def _setup_ui(self) -> None:
        """Sets up the dashboard UI elements."""
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(20)

        # Create KPI cards
        self.stats_grid = QGridLayout()
        self.stats_grid.setHorizontalSpacing(16)
        self.stats_grid.setVerticalSpacing(16)

        self.health_card = StatCard("Equipment Health", "94%", "Stable operating condition")
        self.alert_card = StatCard("Active Alerts", "07", "Requires review")
        self.energy_card = StatCard("Energy Usage", "--- kWh", "Connecting to sensors...")
        self.work_order_card = StatCard("Work Orders", "12", "Scheduled today")

        self.stats_grid.addWidget(self.health_card, 0, 0)
        self.stats_grid.addWidget(self.alert_card, 0, 1)
        self.stats_grid.addWidget(self.energy_card, 0, 2)
        self.stats_grid.addWidget(self.work_order_card, 0, 3)

        root_layout.addLayout(self.stats_grid)

        # Lower panels layout (Activity & Overview)
        lower_section = QHBoxLayout()
        lower_section.setSpacing(16)

        left_panel = self._build_activity_panel()
        right_panel = self._build_overview_panel()

        lower_section.addWidget(left_panel, 2)
        lower_section.addWidget(right_panel, 1)

        root_layout.addLayout(lower_section, 1)

    def _build_activity_panel(self) -> QFrame:
        """Builds the recent industrial events panel."""
        panel = QFrame()
        panel.setObjectName("tableLikePanel")

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(14)

        title = QLabel("Recent Industrial Events")
        title.setObjectName("sectionTitle")

        layout.addWidget(title)
        layout.addWidget(self._event_row("Compressor-02", "High vibration detected", "2 min ago"))
        layout.addWidget(self._event_row("Boiler-01", "Maintenance task completed", "18 min ago"))
        layout.addWidget(self._event_row("CNC-03", "Temperature back to normal range", "42 min ago"))
        layout.addWidget(self._event_row("Packaging-Line-A", "Inspection scheduled", "1 hr ago"))
        layout.addStretch()

        return panel

    def _build_overview_panel(self) -> QFrame:
        """Builds the system overview panel."""
        panel = QFrame()
        panel.setObjectName("tableLikePanel")

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(14)

        title = QLabel("System Overview")
        title.setObjectName("sectionTitle")

        health = QLabel("Factory Health Score: 91/100")
        health.setStyleSheet("font-size: 18px; font-weight: 700; color: #12B76A;")

        details = QLabel(
            "Monitoring 24 connected assets\n"
            "3 production zones\n"
            "MQTT gateway: simulated\n"
            "Anomaly model: standby"
        )
        details.setStyleSheet("color: #98A2B3; font-size: 13px;")
        details.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        developer = QLabel("Developed by Ashkan Motaei")
        developer.setObjectName("developerBadge")

        layout.addWidget(title)
        layout.addWidget(health)
        layout.addWidget(details)
        layout.addStretch()
        layout.addWidget(developer)

        return panel

    def _event_row(self, equipment: str, event: str, time_text: str) -> QFrame:
        """Creates a styled row for recent events."""
        row = QFrame()
        row.setStyleSheet("""
            QFrame {
                background-color: #263753;
                border: 1px solid #3B4D6B;
                border-radius: 7px;
            }
            QFrame:hover {
                background-color: #2D405F;
                border-color: #4B6389;
            }
            QLabel {
                background-color: transparent;
                border: none;
            }
        """)

        layout = QHBoxLayout(row)
        layout.setContentsMargins(12, 10, 12, 10)

        equipment_label = QLabel(equipment)
        equipment_label.setStyleSheet("font-weight: 600; color: #F9FAFB;")

        event_label = QLabel(event)
        event_label.setStyleSheet("color: #98A2B3;")

        time_label = QLabel(time_text)
        time_label.setStyleSheet("color: #2E90FA; font-size: 12px;")

        layout.addWidget(equipment_label, 1)
        layout.addWidget(event_label, 2)
        layout.addWidget(time_label, 0, Qt.AlignmentFlag.AlignRight)

        return row

    @Slot(SensorReadout)
    def _update_live_data(self, data: SensorReadout) -> None:
        """Update UI components with new data from the sensor hub."""
        self.energy_card.value_label.setText(f"{data.energy_consumption:.1f} kWh")

        # Dynamic visual response based on energy consumption levels
        if data.energy_consumption >= 430:
            color = "#F04438"  # Critical (Red)
            status = "High energy consumption"
        elif data.energy_consumption >= 420:
            color = "#F79009"  # Warning (Orange)
            status = "Elevated energy consumption"
        else:
            color = "#12B76A"  # Normal (Green)
            status = "Energy consumption is normal"

        self.energy_card.value_label.setStyleSheet(
            f"background-color: transparent; color: {color}; font-size: 28px; font-weight: 700;"
        )
        self.energy_card.hint_label.setText(
            f"{status} · {data.timestamp:%H:%M:%S}"
        )

    def shutdown(self) -> None:
        """This page doesn't manage its own thread, so no action needed here."""
        pass
