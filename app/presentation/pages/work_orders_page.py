"""
Work Orders Management Page.
Developed by Ashkan Motaei.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from PySide6.QtCore import QDate, QTimer
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QDialog,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.infrastructure.database import EquipmentModel, SessionLocal, WorkOrderModel


class WorkOrderDialog(QDialog):
    """Dialog for creating or editing a work order."""

    def __init__(self, parent=None, work_order_id: Optional[int] = None) -> None:
        super().__init__(parent)
        self.setWindowTitle(
            "Add New Work Order" if work_order_id is None else "Edit Work Order"
        )
        self.setMinimumWidth(450)

        self.work_order_id = work_order_id
        self.db = SessionLocal()

        self._setup_ui()
        if self.work_order_id:
            self.load_data()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        self.equipment_combo = QComboBox()
        self.load_equipment_to_combo()
        self.equipment_combo.setStyleSheet("padding: 8px;")

        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("e.g., Routine Maintenance, Repair")
        self.title_input.setStyleSheet("padding: 8px;")

        self.desc_input = QTextEdit()
        self.desc_input.setPlaceholderText("Detailed description of the task.")
        self.desc_input.setStyleSheet("padding: 8px;")
        self.desc_input.setMinimumHeight(100)

        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["Low", "Medium", "High"])
        self.priority_combo.setStyleSheet("padding: 8px;")

        self.status_combo = QComboBox()
        self.status_combo.addItems(
            ["Open", "In Progress", "Pending", "Completed", "Cancelled"]
        )
        self.status_combo.setStyleSheet("padding: 8px;")

        self.assigned_to_input = QLineEdit()
        self.assigned_to_input.setPlaceholderText("Technician name or ID")
        self.assigned_to_input.setStyleSheet("padding: 8px;")

        self.due_date_edit = QDateEdit()
        self.due_date_edit.setCalendarPopup(True)
        self.due_date_edit.setDate(QDate.currentDate())
        self.due_date_edit.setStyleSheet("padding: 8px;")
        self.due_date_edit.setDisplayFormat("yyyy-MM-dd")

        layout.addWidget(self._create_labeled_widget("Equipment:", self.equipment_combo))
        layout.addWidget(self._create_labeled_widget("Title:", self.title_input))
        layout.addWidget(self._create_labeled_widget("Description:", self.desc_input))
        layout.addWidget(self._create_labeled_widget("Priority:", self.priority_combo))
        layout.addWidget(self._create_labeled_widget("Status:", self.status_combo))
        layout.addWidget(self._create_labeled_widget("Assigned To:", self.assigned_to_input))
        layout.addWidget(self._create_labeled_widget("Due Date:", self.due_date_edit))

        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save)
        self.save_button.setStyleSheet(
            "background-color: #2563EB; color: white; padding: 10px;"
        )

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        cancel_button.setStyleSheet(
            "background-color: #374151; color: white; padding: 10px;"
        )

        button_layout.addStretch()
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(self.save_button)
        layout.addLayout(button_layout)

    def _create_labeled_widget(self, label_text: str, widget: QWidget) -> QFrame:
        frame = QFrame()
        v_layout = QVBoxLayout(frame)
        v_layout.setContentsMargins(0, 0, 0, 0)

        label = QLabel(label_text)
        label.setStyleSheet("font-weight: bold; margin-bottom: 5px;")

        v_layout.addWidget(label)
        v_layout.addWidget(widget)
        return frame

    def load_equipment_to_combo(self) -> None:
        equipment_list = self.db.query(EquipmentModel).all()
        for eq in equipment_list:
            self.equipment_combo.addItem(f"{eq.name} ({eq.id})", eq.id)

    def load_data(self) -> None:
        if not self.work_order_id:
            return

        wo = (
            self.db.query(WorkOrderModel)
            .filter(WorkOrderModel.id == self.work_order_id)
            .first()
        )
        if not wo:
            return

        self.title_input.setText(wo.title)
        self.desc_input.setText(wo.description)
        self.priority_combo.setCurrentText(wo.priority)
        self.status_combo.setCurrentText(wo.status)
        self.assigned_to_input.setText(wo.assigned_to or "")

        if wo.due_date:
            self.due_date_edit.setDate(
                QDate(wo.due_date.year, wo.due_date.month, wo.due_date.day)
            )

        for i in range(self.equipment_combo.count()):
            if self.equipment_combo.itemData(i) == wo.equipment_id:
                self.equipment_combo.setCurrentIndex(i)
                break

        self.setWindowTitle(f"Edit Work Order #{self.work_order_id}")
        self.save_button.setText("Update")

    def save(self) -> None:
        title = self.title_input.text().strip()
        description = self.desc_input.toPlainText().strip()
        priority = self.priority_combo.currentText()
        status = self.status_combo.currentText()
        assigned_to = self.assigned_to_input.text().strip()

        selected_eq_index = self.equipment_combo.currentIndex()
        if selected_eq_index < 0:
            QMessageBox.warning(
                self,
                "Missing Equipment",
                "No equipment selected. Please pick an asset.",
            )
            return

        equipment_id = self.equipment_combo.itemData(selected_eq_index)
        equipment_name = self.equipment_combo.currentText().split(" (")[0]

        if not title or not description or not equipment_id:
            QMessageBox.warning(
                self,
                "Required Fields",
                "Title, Description, and Equipment are required.",
            )
            return

        qdate = self.due_date_edit.date()
        due_date = datetime(qdate.year(), qdate.month(), qdate.day())

        try:
            if self.work_order_id:
                wo = (
                    self.db.query(WorkOrderModel)
                    .filter(WorkOrderModel.id == self.work_order_id)
                    .first()
                )
                if not wo:
                    QMessageBox.warning(self, "Not Found", "Work order not found.")
                    return

                wo.title = title
                wo.description = description
                wo.priority = priority
                wo.status = status
                wo.assigned_to = assigned_to if assigned_to else None
                wo.due_date = due_date
                wo.equipment_id = equipment_id
                wo.equipment_name = equipment_name
                wo.completed_at = datetime.now() if status == "Completed" else None

            else:
                new_wo = WorkOrderModel(
                    equipment_id=equipment_id,
                    equipment_name=equipment_name,
                    title=title,
                    description=description,
                    priority=priority,
                    status=status,
                    assigned_to=assigned_to if assigned_to else None,
                    due_date=due_date,
                    completed_at=datetime.now() if status == "Completed" else None,
                )
                self.db.add(new_wo)

            self.db.commit()
            self.accept()

        except Exception as e:
            self.db.rollback()
            QMessageBox.critical(self, "Save Error", f"Error saving work order:\n{e}")

    def reject(self) -> None:
        self.db.close()
        super().reject()

    def accept(self) -> None:
        self.db.close()
        super().accept()


class WorkOrdersPage(QWidget):
    """Page for managing maintenance work orders."""

    def __init__(self) -> None:
        super().__init__()
        self._setup_ui()
        self.load_data()

        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.load_data)
        self.refresh_timer.start(45_000)

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)

        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(10)

        title_label = QLabel("Work Orders")
        title_label.setObjectName("sectionTitle")

        self.add_button = QPushButton("Add Work Order")
        self.add_button.setObjectName("navButton")
        self.add_button.setStyleSheet(
            "background-color: #12B76A; color: white; padding: 8px 16px;"
        )
        self.add_button.clicked.connect(self.open_add_dialog)

        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.add_button)
        layout.addLayout(header_layout)

        filter_layout = QHBoxLayout()
        filter_layout.setContentsMargins(0, 0, 0, 0)
        filter_layout.setSpacing(10)

        status_label = QLabel("Status:")
        status_label.setStyleSheet("color: #94A3B8; font-weight: bold;")

        self.status_combo = QComboBox()
        self.status_combo.addItems(
            ["All", "Open", "In Progress", "Pending", "Completed", "Cancelled"]
        )
        self.status_combo.setStyleSheet(
            "padding: 6px; background-color: #1E293B; "
            "border: 1px solid #334155; color: #CBD5E1; border-radius: 6px;"
        )
        self.status_combo.currentIndexChanged.connect(self.apply_filters)

        priority_label = QLabel("Priority:")
        priority_label.setStyleSheet("color: #94A3B8; font-weight: bold;")

        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["All", "Low", "Medium", "High"])
        self.priority_combo.setStyleSheet(
            "padding: 6px; background-color: #1E293B; "
            "border: 1px solid #334155; color: #CBD5E1; border-radius: 6px;"
        )
        self.priority_combo.currentIndexChanged.connect(self.apply_filters)

        filter_layout.addWidget(status_label)
        filter_layout.addWidget(self.status_combo)
        filter_layout.addSpacing(20)
        filter_layout.addWidget(priority_label)
        filter_layout.addWidget(self.priority_combo)
        filter_layout.addStretch()
        layout.addLayout(filter_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(
            [
                "ID",
                "Equipment",
                "Title",
                "Priority",
                "Status",
                "Assigned To",
                "Due Date",
                "Actions",
            ]
        )

        self.table.setStyleSheet(
            """
            QTableWidget {
                background-color: #1E293B;
                border: 1px solid #334155;
                gridline-color: #334155;
                border-radius: 8px;
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
                padding: 12px;
                border-bottom: 1px solid #334155;
            }
            QTableWidget::item:selected {
                background-color: #263753;
                color: #FFFFFF;
            }
            """
        )

        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        layout.addWidget(self.table)

    def load_data(self) -> None:
        """Load work orders from the database based on filters."""
        status_filter = self.status_combo.currentText()
        priority_filter = self.priority_combo.currentText()

        db = SessionLocal()
        try:
            query = db.query(WorkOrderModel)

            if status_filter != "All":
                query = query.filter(WorkOrderModel.status == status_filter)
            if priority_filter != "All":
                query = query.filter(WorkOrderModel.priority == priority_filter)

            work_orders = query.order_by(WorkOrderModel.created_at.desc()).all()

        finally:
            db.close()

        self.table.setUpdatesEnabled(False)
        self.table.setSortingEnabled(False)

        try:
            self.table.setRowCount(0)

            for row_idx, wo in enumerate(work_orders):
                self.table.insertRow(row_idx)

                due_date_str = wo.due_date.strftime("%Y-%m-%d") if wo.due_date else "N/A"
                assigned_to_str = wo.assigned_to if wo.assigned_to else "Unassigned"

                id_item = QTableWidgetItem(str(wo.id))
                eq_item = QTableWidgetItem(f"{wo.equipment_name} ({wo.equipment_id})")
                title_item = QTableWidgetItem(wo.title)
                prio_item = QTableWidgetItem(wo.priority)
                stat_item = QTableWidgetItem(wo.status)
                assign_item = QTableWidgetItem(assigned_to_str)
                due_item = QTableWidgetItem(due_date_str)

                self._style_table_item(prio_item, wo.priority)
                self._style_table_item(stat_item, wo.status)

                self.table.setItem(row_idx, 0, id_item)
                self.table.setItem(row_idx, 1, eq_item)
                self.table.setItem(row_idx, 2, title_item)
                self.table.setItem(row_idx, 3, prio_item)
                self.table.setItem(row_idx, 4, stat_item)
                self.table.setItem(row_idx, 5, assign_item)
                self.table.setItem(row_idx, 6, due_item)
                self.table.setCellWidget(
                    row_idx, 7, self._create_action_buttons(wo.id)
                )

        finally:
            self.table.setUpdatesEnabled(True)
            self.table.setSortingEnabled(True)

    def _style_table_item(self, item: QTableWidgetItem, value: str) -> None:
        """Apply color styling to table items based on value."""
        color_map = {
            "Low": QColor("#38BDF8"),
            "Medium": QColor("#FBBF24"),
            "High": QColor("#F87171"),
            "Open": QColor("#F87171"),
            "In Progress": QColor("#FBBF24"),
            "Pending": QColor("#FACC15"),
            "Completed": QColor("#34D399"),
            "Cancelled": QColor("#94A3B8"),
        }

        color = color_map.get(value)
        if color:
            item.setForeground(color)

        if value == "Completed":
            item.setBackground(QColor(40, 55, 80))

    def _create_action_buttons(self, work_order_id: int) -> QWidget:
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        edit_button = QPushButton("Edit")
        edit_button.setStyleSheet(
            "background-color: #374151; color: white; padding: 6px 12px; border-radius: 5px;"
        )
        edit_button.clicked.connect(lambda: self.open_edit_dialog(work_order_id))

        delete_button = QPushButton("Delete")
        delete_button.setStyleSheet(
            "background-color: #F04438; color: white; padding: 6px 12px; border-radius: 5px;"
        )
        delete_button.clicked.connect(lambda: self.delete_work_order(work_order_id))

        layout.addWidget(edit_button)
        layout.addWidget(delete_button)
        layout.addStretch()
        return widget

    def apply_filters(self) -> None:
        self.load_data()

    def open_add_dialog(self) -> None:
        dialog = WorkOrderDialog(self)
        if dialog.exec() == QDialog.Accepted:
            self.load_data()

    def open_edit_dialog(self, work_order_id: int) -> None:
        dialog = WorkOrderDialog(self, work_order_id=work_order_id)
        if dialog.exec() == QDialog.Accepted:
            self.load_data()

    def delete_work_order(self, work_order_id: int) -> None:
        reply = QMessageBox.question(
            self,
            "Delete Work Order",
            f"Are you sure you want to delete work order #{work_order_id}?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return

        db = SessionLocal()
        try:
            wo = (
                db.query(WorkOrderModel)
                .filter(WorkOrderModel.id == work_order_id)
                .first()
            )
            if wo:
                db.delete(wo)
                db.commit()
                self.load_data()
            else:
                QMessageBox.information(
                    self, "Not Found", f"Work Order #{work_order_id} not found."
                )
        except Exception as e:
            db.rollback()
            QMessageBox.critical(self, "Delete Error", f"Error deleting work order:\n{e}")
        finally:
            db.close()

    def shutdown(self) -> None:
        """Clean up resources."""
        if self.refresh_timer.isActive():
            self.refresh_timer.stop()
