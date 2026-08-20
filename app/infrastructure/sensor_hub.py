"""
Centralized Sensor Data Hub Service.
Generates simulated telemetry and emits alerts safely.
Developed by Ashkan Motaei.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional

from PySide6.QtCore import QObject, QThread, Signal, Slot


@dataclass
class SensorReadout:
    """Model for sensor data points."""

    equipment_id: str
    temperature: float
    vibration: float
    energy_consumption: float
    timestamp: datetime


class SensorWorker(QObject):
    """Worker running in a dedicated thread to simulate telemetry."""

    data_generated = Signal(SensorReadout)
    finished = Signal()

    def __init__(self) -> None:
        super().__init__()
        self._running = False

        self._temperature = 74.5
        self._vibration = 4.1
        self._energy_consumption = 422.0

    @Slot()
    def run(self) -> None:
        """Main simulation loop."""
        self._running = True

        while self._running:
            thread = self.thread()
            if thread and thread.isInterruptionRequested():
                break

            self._temperature = self._next_value(
                current=self._temperature,
                min_value=68.0,
                max_value=90.0,
                step=0.85,
            )

            self._vibration = self._next_value(
                current=self._vibration,
                min_value=3.0,
                max_value=5.5,
                step=0.15,
            )

            self._energy_consumption = self._next_value(
                current=self._energy_consumption,
                min_value=405.0,
                max_value=440.0,
                step=2.5,
            )

            readout = SensorReadout(
                equipment_id="EQ-001",
                temperature=round(self._temperature, 2),
                vibration=round(self._vibration, 2),
                energy_consumption=round(self._energy_consumption, 2),
                timestamp=datetime.now(),
            )

            self.data_generated.emit(readout)

            # Sleep safely inside worker thread
            QThread.msleep(1500)

        self._running = False
        self.finished.emit()

    def stop(self) -> None:
        """Stop the worker loop."""
        self._running = False

    @staticmethod
    def _next_value(
        current: float,
        min_value: float,
        max_value: float,
        step: float,
    ) -> float:
        """Generate bounded random walk telemetry."""
        candidate = current + random.uniform(-step, step)
        return max(min_value, min(max_value, candidate))


class SensorDataHub(QObject):
    """
    Central hub for sensor telemetry.
    Emits raw telemetry to UI and normalized alerts to AlertsManager.
    """

    data_available = Signal(SensorReadout)
    alert_generated = Signal(dict)

    def __init__(self) -> None:
        super().__init__()

        self.equipment_status: Dict[str, Dict] = {}
        self.alert_cooldown_seconds = 60

        self.worker_thread = QThread()
        self.worker = SensorWorker()
        self.worker.moveToThread(self.worker_thread)

        self.worker_thread.started.connect(self.worker.run)
        self.worker.data_generated.connect(self._process_sensor_data)
        self.worker.finished.connect(self.worker_thread.quit)

    @Slot(SensorReadout)
    def _process_sensor_data(self, data: SensorReadout) -> None:
        """Process telemetry and emit alerts if needed."""
        equipment_id = data.equipment_id

        if equipment_id not in self.equipment_status:
            self.equipment_status[equipment_id] = {
                "health_score": 100.0,
                "status": "Operational",
                "last_readout": None,
                "last_alerts": {},
            }

        state = self.equipment_status[equipment_id]
        state["last_readout"] = data

        health_score = 95.0
        status = "Operational"

        if data.temperature > 85.0:
            health_score = 65.0
            status = "Critical"
            self._emit_alert_throttled(
                equipment_id=equipment_id,
                alert_type="Overheating",
                severity="Critical",
                message=(
                    f"Temperature reached {data.temperature:.1f}°C, "
                    "exceeding the critical threshold of 85°C."
                ),
                timestamp=data.timestamp,
            )

        elif data.vibration > 5.0:
            health_score = 78.0
            status = "Warning"
            self._emit_alert_throttled(
                equipment_id=equipment_id,
                alert_type="High Vibration",
                severity="Medium",
                message=(
                    f"Vibration is {data.vibration:.2f} mm/s, "
                    "exceeding normal limits."
                ),
                timestamp=data.timestamp,
            )

        elif data.energy_consumption > 435.0:
            health_score = 84.0
            status = "Warning"
            self._emit_alert_throttled(
                equipment_id=equipment_id,
                alert_type="High Power Load",
                severity="Low",
                message=(
                    f"Energy consumption is {data.energy_consumption:.1f} kWh, "
                    "above the expected range."
                ),
                timestamp=data.timestamp,
            )

        state["health_score"] = health_score
        state["status"] = status

        self.data_available.emit(data)

    def _emit_alert_throttled(
        self,
        equipment_id: str,
        alert_type: str,
        severity: str,
        message: str,
        timestamp: datetime,
    ) -> None:
        """Emit alert with cooldown protection to avoid flooding."""
        state = self.equipment_status.setdefault(
            equipment_id,
            {
                "health_score": 100.0,
                "status": "Operational",
                "last_readout": None,
                "last_alerts": {},
            },
        )

        last_alerts = state.setdefault("last_alerts", {})
        now = datetime.now()
        last_alert_time: Optional[datetime] = last_alerts.get(alert_type)

        if last_alert_time is not None:
            elapsed_seconds = (now - last_alert_time).total_seconds()
            if elapsed_seconds < self.alert_cooldown_seconds:
                return

        last_alerts[alert_type] = now

        self.alert_generated.emit(
            {
                "equipment_id": equipment_id,
                "alert_type": alert_type,
                "severity": severity,
                "message": message,
                "timestamp": timestamp,
            }
        )

    def start(self) -> None:
        """Start worker thread."""
        if not self.worker_thread.isRunning():
            self.worker_thread.start()

    def stop(self) -> None:
        """Gracefully stop worker thread."""
        if self.worker_thread.isRunning():
            self.worker.stop()
            self.worker_thread.requestInterruption()
            self.worker_thread.quit()
            self.worker_thread.wait(2000)
