# IndustrialPulse Monitoring

A modern industrial desktop monitoring platform built with **Python**, **PySide6**, **SQLAlchemy**, and **SQLite**.  
IndustrialPulse is designed for **real-time telemetry visualization**, **alert management**, and **predictive maintenance workflows** with a focus on **responsive UI**, **thread-safe data handling**, and **clean architecture**.

---

## Overview

IndustrialPulse is a cross-platform desktop application for industrial operations monitoring.  
It simulates and processes telemetry data, detects critical conditions, generates alerts, and automatically creates maintenance work orders when high-severity events occur.

The project was developed with a strong focus on:

- maintainable architecture
- non-blocking user interface
- thread-safe database access
- scalable UI composition
- professional desktop software standards

---

## Key Features

### Real-Time Monitoring
- Live industrial telemetry simulation
- Continuous sensor data processing
- Dashboard-style operational overview

### Alert Management
- Severity-based alerts: Low, Medium, High, Critical
- Acknowledgment workflow
- Color-coded UI feedback
- Filterable alerts table

### Predictive Maintenance
- Automatic Work Order generation from critical alerts
- Duplicate prevention for active alert-driven work orders
- Work order lifecycle tracking

### Responsive Desktop Architecture
- Multi-threaded background processing
- `QThread`-based sensor simulation
- `QueuedConnection` for safe cross-thread DB updates
- UI update optimization to avoid freezes

### Professional UI
- Custom dark theme
- Modern Qt-based layout
- Clear navigation structure
- Developer-friendly and recruiter-friendly design

---

## Technology Stack

- **Python 3.10+**
- **PySide6 / Qt**
- **SQLAlchemy**
- **SQLite**
- **PyInstaller**
- Optional: `pandas`, `numpy`, `scikit-learn` for future analytics and anomaly detection

---

## Architecture

IndustrialPulse follows a modular desktop application structure:
```text
app/
├── infrastructure/
│   ├── database.py
│   ├── alerts_manager.py
│   └── sensor_hub.py
├── presentation/
│   ├── main_window.py
│   ├── pages/
│   │   ├── dashboard_page.py
│   │   ├── alerts_page.py
│   │   ├── work_orders_page.py
│   │   └── monitoring_page.py
│   └── styles/
│       └── theme.py
└── main.py
