"""
Live monitoring page for IndustrialPulse.
Developed by Ashkan Motaei.
"""

from __future__ import annotations

import numpy as np
import pyqtgraph as pg
from PySide6.QtCore import QThread, Slot
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from app.infrastructure.sensor_hub import SensorDataHub, SensorReadout


class MonitoringPage(QWidget):
    """Page for displaying real-time sensor telemetry with live charts."""

    def __init__(self, sensor_hub: SensorDataHub) -> None:
        super().__init__()
        self.sensor_hub = sensor_hub

        self.max_points = 100

        self.temp_data = np.full(self.max_points, 74.5)
        self.vibe_data = np.full(self.max_points, 4.1)
        self.energy_data = np.full(self.max_points, 422.0)

        self._setup_ui()

        # Connect to the central sensor hub
        self.sensor_hub.data_available.connect(self._update_charts)

    def _setup_ui(self) -> None:
        """Initialize the layout and create charts."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        self.temp_panel = self._create_chart_panel(
            title="Main Compressor Temperature",
            color="#F04438",
            unit="°C",
            y_range=(65, 90),
            initial_data=self.temp_data,
        )
        self.vibe_panel = self._create_chart_panel(
            title="Vibration Analysis (X-Axis)",
            color="#2E90FA",
            unit="mm/s",
            y_range=(3, 6),
            initial_data=self.vibe_data,
        )
        self.energy_panel = self._create_chart_panel(
            title="Live Power Load",
            color="#12B76A",
            unit="kWh",
            y_range=(400, 440),
            initial_data=self.energy_data,
        )

        layout.addWidget(self.temp_panel)
        layout.addWidget(self.vibe_panel)
        layout.addWidget(self.energy_panel)

    def _create_chart_panel(
        self,
        title: str,
        color: str,
        unit: str,
        y_range: tuple[float, float],
        initial_data: np.ndarray,
    ) -> QFrame:
        """Create a styled chart panel with header and plot."""

        frame = QFrame()
        frame.setObjectName("tableLikePanel")

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        header_layout = QHBoxLayout()

        title_label = QLabel(title)
        title_label.setObjectName("sectionTitle")

        value_label = QLabel(f"{initial_data[-1]:.1f} {unit}")
        value_label.setStyleSheet(
            f"color: {color}; font-weight: 700; font-size: 16px;"
        )

        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(value_label)

        plot_widget = pg.PlotWidget()
        plot_widget.setBackground("#0F172A")
        plot_widget.showGrid(x=True, y=True, alpha=0.18)
        plot_widget.setMenuEnabled(False)
        plot_widget.setMouseEnabled(x=False, y=False)
        plot_widget.hideButtons()

        left_axis = plot_widget.getAxis("left")
        bottom_axis = plot_widget.getAxis("bottom")
        left_axis.setTextPen("#94A3B8")
        bottom_axis.setTextPen("#94A3B8")
        left_axis.setPen("#334155")
        bottom_axis.setPen("#334155")

        plot_widget.setYRange(*y_range)
        plot_widget.setXRange(0, self.max_points - 1)
        plot_widget.setLimits(xMin=0, xMax=self.max_points - 1)

        pen = pg.mkPen(color=color, width=2)
        curve = plot_widget.plot(initial_data, pen=pen)

        layout.addLayout(header_layout)
        layout.addWidget(plot_widget)

        if "Temperature" in title:
            self.temp_curve = curve
            self.temp_value_label = value_label
        elif "Vibration" in title:
            self.vibe_curve = curve
            self.vibe_value_label = value_label
        else:
            self.energy_curve = curve
            self.energy_value_label = value_label

        return frame

    @Slot(SensorReadout)
    def _update_charts(self, data: SensorReadout) -> None:
        """Update chart buffers and redraw curves using data from hub."""

        self.temp_data = np.roll(self.temp_data, -1)
        self.temp_data[-1] = data.temperature
        self.temp_curve.setData(self.temp_data)
        self.temp_value_label.setText(f"{data.temperature:.1f} °C")

        self.vibe_data = np.roll(self.vibe_data, -1)
        self.vibe_data[-1] = data.vibration
        self.vibe_curve.setData(self.vibe_data)
        self.vibe_value_label.setText(f"{data.vibration:.2f} mm/s")

        self.energy_data = np.roll(self.energy_data, -1)
        self.energy_data[-1] = data.energy_consumption
        self.energy_curve.setData(self.energy_data)
        self.energy_value_label.setText(f"{data.energy_consumption:.1f} kWh")

    def shutdown(self) -> None:
        """This page doesn't manage its own thread, hub is managed elsewhere."""
        pass
