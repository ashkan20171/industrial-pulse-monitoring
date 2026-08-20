"""
Equipment Management Page.
Developed by Ashkan Motaei.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QTableWidget, QTableWidgetItem, QHeaderView, QPushButton
)
from app.infrastructure.database import SessionLocal, EquipmentModel


class EquipmentPage(QWidget):
    """Asset management registry with filtering capability."""

    def __init__(self) -> None:
        super().__init__()
        self._setup_ui()
        self.load_data("All")

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)

        # Filter bar
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(10)
        
        self.btn_all = QPushButton("All Assets")
        self.btn_all.setObjectName("navButton")
        self.btn_all.setCheckable(True)
        self.btn_all.setChecked(True)
        self.btn_all.clicked.connect(lambda: self.load_data("All"))

        self.btn_ok = QPushButton("Operational")
        self.btn_ok.setObjectName("navButton")
        self.btn_ok.setCheckable(True)
        self.btn_ok.clicked.connect(lambda: self.load_data("Operational"))

        self.btn_warn = QPushButton("Warning")
        self.btn_warn.setObjectName("navButton")
        self.btn_warn.setCheckable(True)
        self.btn_warn.clicked.connect(lambda: self.load_data("Warning"))

        self.btn_crit = QPushButton("Critical")
        self.btn_crit.setObjectName("navButton")
        self.btn_crit.setCheckable(True)
        self.btn_crit.clicked.connect(lambda: self.load_data("Critical"))

        # Keep buttons in exclusive group behavior manually
        self.filter_buttons = [self.btn_all, self.btn_ok, self.btn_warn, self.btn_crit]
        for btn in self.filter_buttons:
            filter_layout.addWidget(btn)
            
        filter_layout.addStretch()
        layout.addLayout(filter_layout)

        # Table Widget
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Asset ID", "Equipment Name", "Type", "Location", "Health Score", "Status"
        ])
        
        # Apply Table Styling to match Dark Industrial Theme
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #1E293B;
                border: 1px solid #334155;
                gridline-color: #334155;
                border-radius: 8px;
            }
            QHeaderView::section {
                background-color: #0F172A;
                color: #94A3B8;
                padding: 10px;
                border: none;
                border-bottom: 1px solid #334155;
                font-weight: bold;
            }
            QTableWidget::item {
                padding: 12px;
                border-bottom: 1px solid #334155;
            }
            QTableWidget::item:selected {
                background-color: #263753;
                color: #FFFFFF;
            }
        """)
        
        # Table configuration
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        layout.addWidget(self.table)

    def load_data(self, filter_status: str) -> None:
        """Fetch equipment data from SQLite database and populate table."""
        # Handle button toggle states visually
        for btn in self.filter_buttons:
            btn.setChecked(btn.text() == filter_status or (filter_status == "All" and btn.text() == "All Assets"))

        db = SessionLocal()
        query = db.query(EquipmentModel)
        
        if filter_status != "All":
            query = query.filter(EquipmentModel.status == filter_status)
            
        assets = query.all()
        db.close()

        self.table.setRowCount(0)
        for row_idx, asset in enumerate(assets):
            self.table.insertRow(row_idx)
            
            # Write cells
            self.table.setItem(row_idx, 0, QTableWidgetItem(asset.id))
            self.table.setItem(row_idx, 1, QTableWidgetItem(asset.name))
            self.table.setItem(row_idx, 2, QTableWidgetItem(asset.type))
            self.table.setItem(row_idx, 3, QTableWidgetItem(asset.location))
            self.table.setItem(row_idx, 4, QTableWidgetItem(f"{asset.health_score:.1f}%"))
            
            # Status Cell with color coding
            status_item = QTableWidgetItem(asset.status)
            if asset.status == "Operational":
                status_item.setForeground(Qt.green)
            elif asset.status == "Warning":
                status_item.setForeground(Qt.yellow)
            else:
                status_item.setForeground(Qt.red)
            self.table.setItem(row_idx, 5, status_item)
