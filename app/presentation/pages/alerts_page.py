"""
Alerts Center Page.
Developed by Ashkan Motaei.
"""

from __future__ import annotations

from typing import Dict, Optional

from PySide6.QtCore import QTimer, Slot
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.infrastructure.alerts_manager import AlertsManager


class AlertsPage(QWidget):
    """Displays, filters, and acknowledges system alerts."""

    def __init__(self, alerts_manager: AlertsManager) -> None:
        super().__init__()

        # Injected singleton manager
        self.alerts_manager = alerts_manager

        self._setup_ui()

        # Refresh timer (Set to 30s to keep UI lightweight)
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.load_alerts)
        self.refresh_timer.start(30_000)

        self.load_alerts()

    def _setup_ui(self) -> None:
        """Create the Alerts Center interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)

        # Header bar
        header_layout = QHBoxLayout()
        header_layout.setSpacing(10)

        title_label = QLabel("Alerts Center")
        title_label.setObjectName("sectionTitle")

        self.total_alerts_label = QLabel("Alerts: 0")
        self.total_alerts_label.setStyleSheet("color: #94A3B8; font-weight: bold;")

        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.setObjectName("refreshButton")
        self.refresh_button.clicked.connect(self.load_alerts)

        header_layout.addWidget(title_label)
        header_layout.addWidget(self.total_alerts_label)
        header_layout.addStretch()
        header_layout.addWidget(self.refresh_button)

        layout.addLayout(header_layout)

        # Severity filter bar
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(8)

        self.filter_buttons: Dict[str, QPushButton] = {}

        for option in ["All", "Low", "Medium", "High", "Critical"]:
            button = QPushButton(option)
            button.setCheckable(True)
            button.setObjectName("filterButton")
            button.setChecked(option == "All")
            button.clicked.connect(
                lambda checked=False, value=option: self.filter_alerts(value)
            )
            self.filter_buttons[option] = button
            filter_layout.addWidget(button)

        filter_layout.addStretch()
        layout.addLayout(filter_layout)

        # Alerts Table
        self.alert_table = QTableWidget()
        self.alert_table.setColumnCount(9)
        self.alert_table.setHorizontalHeaderLabels(
            [
                "ID",
                "Timestamp",
                "Equipment",
                "Type",
                "Severity",
                "Message",
                "Status",
                "Work Order",
                "Actions",
            ]
        )

        self.alert_table.setStyleSheet(
            """
            QTableWidget {
                background-color: #1E293B;
                border: 1px solid #334155;
                gridline-color: #334155;
                border-radius: 8px;
                color: #E2E8F0;
            }

            QHeaderView::section {
                background-color: #0F172A;
                color: #98A2B3;
                padding: 10px;
                border: none;
                border-bottom: 1px solid #334155;
                font-weight: bold;
            }

            QTableWidget::item {
                padding: 10px;
                border-bottom: 1px solid #334155;
            }

            QTableWidget::item:selected {
                background-color: #263753;
                color: #FFFFFF;
            }

            QPushButton#filterButton {
                padding: 8px 16px;
                border: 1px solid #3B4D6B;
                border-radius: 6px;
                background-color: #1E293B;
                color: #CBD5E1;
                font-weight: 500;
            }

            QPushButton#filterButton:checked {
                background-color: #2563EB;
                border-color: #2563EB;
                color: #FFFFFF;
            }

            QPushButton#filterButton:hover {
                background-color: #374151;
            }

            QPushButton#refreshButton {
                background-color: #2563EB;
                color: white;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
            }

            QPushButton#refreshButton:hover {
                background-color: #1D4ED8;
            }
            """
        )

        self.alert_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.alert_table.verticalHeader().setVisible(False)
        self.alert_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.alert_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.alert_table.setWordWrap(True)

        layout.addWidget(self.alert_table)

    @Slot()
    def load_alerts(self) -> None:
        """Load alerts from database without freezing the render engine."""
        selected_filter = self._get_selected_filter()

        # Disable rendering updates during bulk population to prevent UI freeze
        self.alert_table.setUpdatesEnabled(False)
        self.alert_table.setSortingEnabled(False)

        try:
            alerts_data = self.alerts_manager.get_alerts(filter_severity=selected_filter)

            self.alert_table.setRowCount(0)
            self.total_alerts_label.setText(f"Alerts: {len(alerts_data)}")

            for row_index, alert in enumerate(alerts_data):
                self.alert_table.insertRow(row_index)

                alert_id = alert["id"]
                timestamp = alert.get("timestamp")
                timestamp_text = (
                    timestamp.strftime("%Y-%m-%d %H:%M:%S") if timestamp else "N/A"
                )

                is_acknowledged = bool(alert.get("is_acknowledged", False))
                status_text = "Acknowledged" if is_acknowledged else "Open"

                id_item = QTableWidgetItem(str(alert_id))
                timestamp_item = QTableWidgetItem(timestamp_text)
                equipment_item = QTableWidgetItem(
                    f"{alert.get('equipment_name', 'Unknown')} ({alert.get('equipment_id', 'N/A')})"
                )
                type_item = QTableWidgetItem(str(alert.get("alert_type", "Unknown")))

                severity = str(alert.get("severity", "Unknown"))
                severity_item = QTableWidgetItem(severity)
                message_item = QTableWidgetItem(str(alert.get("message", "")))
                status_item = QTableWidgetItem(status_text)

                # Color styles
                severity_item.setForeground(self._get_severity_color(severity))
                status_item.setForeground(
                    QColor("#34D399") if is_acknowledged else QColor("#F87171")
                )

                work_order = self.alerts_manager.get_active_work_order_for_alert(
                    alert_id
                )
                work_order_item = self._build_work_order_item(work_order)

                self.alert_table.setItem(row_index, 0, id_item)
                self.alert_table.setItem(row_index, 1, timestamp_item)
                self.alert_table.setItem(row_index, 2, equipment_item)
                self.alert_table.setItem(row_index, 3, type_item)
                self.alert_table.setItem(row_index, 4, severity_item)
                self.alert_table.setItem(row_index, 5, message_item)
                self.alert_table.setItem(row_index, 6, status_item)
                self.alert_table.setItem(row_index, 7, work_order_item)

                action_widget = self._create_action_widget(
                    alert_id=alert_id,
                    is_acknowledged=is_acknowledged,
                )
                self.alert_table.setCellWidget(row_index, 8, action_widget)

        finally:
            self.alert_table.setUpdatesEnabled(True)
            self.alert_table.setSortingEnabled(True)

    def _build_work_order_item(self, work_order: Optional[Dict]) -> QTableWidgetItem:
        """Create item representing linked work order."""
        if work_order:
            item = QTableWidgetItem(f"#{work_order['id']} - {work_order['status']}")
            item.setForeground(QColor("#FBBF24"))
            item.setToolTip(work_order.get("title", ""))
            return item

        item = QTableWidgetItem("None")
        item.setForeground(QColor("#94A3B8"))
        return item

    def _create_action_widget(self, alert_id: int, is_acknowledged: bool) -> QWidget:
        """Create action buttons for a row."""
        widget = QWidget()
        action_layout = QHBoxLayout(widget)
        action_layout.setContentsMargins(2, 2, 2, 2)
        action_layout.setSpacing(5)

        acknowledge_button = QPushButton("Acknowledge")
        acknowledge_button.setObjectName("acknowledgeButton")
        acknowledge_button.setEnabled(not is_acknowledged)
        acknowledge_button.setStyleSheet(
            """
            QPushButton#acknowledgeButton {
                background-color: #F79009;
                color: white;
                padding: 6px 10px;
                border-radius: 5px;
            }

            QPushButton#acknowledgeButton:hover {
                background-color: #D97706;
            }

            QPushButton#acknowledgeButton:disabled {
                background-color: #475569;
                color: #CBD5E1;
            }
            """
        )
        acknowledge_button.clicked.connect(
            lambda checked=False, current_id=alert_id: self.acknowledge_alert(
                current_id
            )
        )

        action_layout.addWidget(acknowledge_button)
        action_layout.addStretch()
        return widget

    def _get_selected_filter(self) -> str:
        """Return the active severity filter."""
        for option, button in self.filter_buttons.items():
            if button.isChecked():
                return option
        return "All"

    def filter_alerts(self, selected_option: str) -> None:
        """Filter alerts based on user selection."""
        for option, button in self.filter_buttons.items():
            button.setChecked(option == selected_option)
        self.load_alerts()

    @Slot(int)
    def acknowledge_alert(self, alert_id: int) -> None:
        """Acknowledge an alert and update table in-place."""
        user_name = "Ashkan Motaei"

        success = self.alerts_manager.acknowledge_alert_in_db(
            alert_id=alert_id,
            user_name=user_name,
        )

        if not success:
            QMessageBox.warning(
                self,
                "Acknowledgment Failed",
                f"Alert #{alert_id} could not be acknowledged.",
            )
            return

        # Immediate row status update without full table reload
        for row_index in range(self.alert_table.rowCount()):
            id_item = self.alert_table.item(row_index, 0)
            if not id_item:
                continue

            if int(id_item.text()) != alert_id:
                continue

            status_item = self.alert_table.item(row_index, 6)
            if status_item:
                status_item.setText("Acknowledged")
                status_item.setForeground(QColor("#34D399"))

            action_widget = self.alert_table.cellWidget(row_index, 8)
            if action_widget:
                for button in action_widget.findChildren(QPushButton):
                    if button.text() == "Acknowledge":
                        button.setEnabled(False)
                        break
            break

    @staticmethod
    def _get_severity_color(severity: str) -> QColor:
        """Return distinct color for each severity level."""
        colors = {
            "Low": "#38BDF8",
            "Medium": "#FBBF24",
            "High": "#FB923C",
            "Critical": "#F87171",
        }
        return QColor(colors.get(severity, "#94A3B8"))

    def shutdown(self) -> None:
        """Halt timers cleanly."""
        if self.refresh_timer.isActive():
            self.refresh_timer.stop()
