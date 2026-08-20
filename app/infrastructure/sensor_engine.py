"""
Sensor Data Engine Simulator.
Generates realistic industrial sensor data in a background thread.
"""

from __future__ import annotations

import random
import time
from dataclasses import dataclass
from datetime import datetime

from PySide6.QtCore import QObject, Signal


@dataclass
class SensorReadout:
    """Model for sensor data points."""

    equipment_id: str
    temperature: float
    vibration: float
    energy_consumption: float
    timestamp: datetime


class SensorWorker(QObject):
    """Worker that simulates live industrial telemetry."""

    data_received = Signal(SensorReadout)

    def __init__(self) -> None:
        super().__init__()
        self._running = True

        self._temperature = 74.5
        self._vibration = 4.1
        self._energy_consumption = 422.0

    def run(self) -> None:
        """Main simulation loop."""

        while self._running:
            self._temperature = self._next_value(
                current=self._temperature,
                min_value=68.0,
                max_value=86.0,
                step=0.9,
            )
            self._vibration = self._next_value(
                current=self._vibration,
                min_value=3.2,
                max_value=5.4,
                step=0.18,
            )
            self._energy_consumption = self._next_value(
                current=self._energy_consumption,
                min_value=408.0,
                max_value=438.0,
                step=2.8,
            )

            readout = SensorReadout(
                equipment_id="Main-Compressor-01",
                temperature=self._temperature,
                vibration=self._vibration,
                energy_consumption=self._energy_consumption,
                timestamp=datetime.now(),
            )

            self.data_received.emit(readout)
            time.sleep(1.5)

    def stop(self) -> None:
        """Stop the simulation loop."""
        self._running = False

    @staticmethod
    def _next_value(
        current: float,
        min_value: float,
        max_value: float,
        step: float,
    ) -> float:
        """Generate the next bounded telemetry value."""

        next_value = current + random.uniform(-step, step)
        return max(min_value, min(max_value, next_value))
