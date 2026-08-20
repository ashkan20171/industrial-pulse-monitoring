"""
Alerts Manager for IndustrialPulse.
Handles alert persistence, acknowledgment, and automatic work orders.
Developed by Ashkan Motaei.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Dict, List, Optional

from PySide6.QtCore import QObject, Slot
from sqlalchemy.orm import Session

from app.infrastructure.database import (
    SessionLocal,
    AlertModel,
    EquipmentModel,
    WorkOrderModel,
)


class AlertsManager(QObject):
    """
    Handles database operations for alerts and maintenance work orders.
    """

    ACTIVE_WORK_ORDER_STATUSES = (
        "Open",
        "In Progress",
        "Pending",
    )

    TERMINAL_WORK_ORDER_STATUSES = (
        "Completed",
        "Cancelled",
    )

    def __init__(self) -> None:
        super().__init__()

    # ------------------------------------------------------------------
    # Alert creation
    # ------------------------------------------------------------------

    @Slot(dict)
    def save_alert_to_db(self, alert_data: Dict) -> None:
        """
        Save an alert and optionally create an automatic Work Order.

        A Critical alert automatically creates a High-priority Work Order.
        Duplicate active Work Orders are not created.

        Required alert_data keys:
            equipment_id
            alert_type
            severity
            message

        Optional keys:
            equipment_name
            timestamp
        """
        db: Session = SessionLocal()

        try:
            equipment_id = str(alert_data["equipment_id"]).strip()
            alert_type = str(alert_data["alert_type"]).strip()
            severity = str(alert_data["severity"]).strip()
            message = str(alert_data["message"]).strip()
            timestamp = alert_data.get("timestamp") or datetime.now()

            if not equipment_id:
                raise ValueError("equipment_id cannot be empty.")

            if not alert_type:
                raise ValueError("alert_type cannot be empty.")

            if not severity:
                raise ValueError("severity cannot be empty.")

            if not message:
                raise ValueError("message cannot be empty.")

            equipment = (
                db.query(EquipmentModel)
                .filter(EquipmentModel.id == equipment_id)
                .first()
            )

            if equipment:
                equipment_name = equipment.name

                # Keep equipment state synchronized with alert severity.
                self._update_equipment_status(
                    equipment=equipment,
                    severity=severity,
                )
            else:
                equipment_name = alert_data.get(
                    "equipment_name",
                    "Unknown Equipment",
                )

                print(
                    f"Warning: Equipment '{equipment_id}' was not found. "
                    "Alert will be saved without equipment relation."
                )

            alert = AlertModel(
                equipment_id=equipment_id,
                equipment_name=equipment_name,
                alert_type=alert_type,
                severity=severity,
                message=message,
                timestamp=timestamp,
                is_acknowledged=False,
            )

            db.add(alert)

            # Generate Alert ID before creating a related Work Order.
            db.flush()

            if (
                severity.lower() == "critical"
                and equipment is not None
            ):
                self._create_critical_work_order_if_needed(
                    db=db,
                    alert=alert,
                    equipment=equipment,
                )

            db.commit()

            print(
                f"Alert saved successfully: "
                f"#{alert.id} | {severity} | {alert_type}"
            )

        except KeyError as error:
            db.rollback()
            print(
                f"Cannot save alert. Required field is missing: {error}"
            )

        except Exception as error:
            db.rollback()
            print(f"Error saving alert to database: {error}")

        finally:
            db.close()

    # ------------------------------------------------------------------
    # Automatic Work Order creation
    # ------------------------------------------------------------------

    def _create_critical_work_order_if_needed(
        self,
        db: Session,
        alert: AlertModel,
        equipment: EquipmentModel,
    ) -> Optional[WorkOrderModel]:
        """
        Create a Work Order for a Critical alert if no active duplicate exists.
        """

        existing_work_order = self._find_active_work_order_for_alert(
            db=db,
            alert=alert,
        )

        if existing_work_order:
            print(
                f"Duplicate prevention: active Work Order "
                f"#{existing_work_order.id} already exists for "
                f"Alert #{alert.id}."
            )
            return existing_work_order

        work_order = self._build_work_order_from_alert(
            alert=alert,
            equipment=equipment,
        )

        db.add(work_order)
        db.flush()

        print(
            f"Automatic Work Order created: "
            f"#{work_order.id} for Alert #{alert.id}"
        )

        return work_order

    def _build_work_order_from_alert(
        self,
        alert: AlertModel,
        equipment: EquipmentModel,
    ) -> WorkOrderModel:
        """
        Build a Work Order object from an Alert.
        """

        due_date = alert.timestamp + timedelta(hours=24)

        return WorkOrderModel(
            equipment_id=equipment.id,
            equipment_name=equipment.name,
            title=f"Critical Alert: {alert.alert_type}",
            description=(
                f"Automatically created from Critical Alert "
                f"#{alert.id}.\n\n"
                f"Equipment: {equipment.name} ({equipment.id})\n"
                f"Alert Type: {alert.alert_type}\n"
                f"Severity: {alert.severity}\n"
                f"Message: {alert.message}\n"
                f"Alert Time: "
                f"{alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                "Required actions:\n"
                "1. Inspect the equipment immediately.\n"
                "2. Identify the root cause.\n"
                "3. Perform corrective maintenance.\n"
                "4. Document the performed action."
            ),
            priority="High",
            status="Open",
            assigned_to=None,
            created_at=datetime.now(),
            due_date=due_date,
            completed_at=None,
        )

    def _find_active_work_order_for_alert(
        self,
        db: Session,
        alert: AlertModel,
    ) -> Optional[WorkOrderModel]:
        """
        Find an active Work Order related to an Alert.

        The Alert ID is stored in the Work Order description.
        """

        alert_marker = f"Critical Alert #{alert.id}"

        return (
            db.query(WorkOrderModel)
            .filter(
                WorkOrderModel.equipment_id == alert.equipment_id,
                WorkOrderModel.title
                == f"Critical Alert: {alert.alert_type}",
                WorkOrderModel.description.contains(alert_marker),
                WorkOrderModel.status.in_(
                    self.ACTIVE_WORK_ORDER_STATUSES
                ),
            )
            .order_by(
                WorkOrderModel.created_at.desc()
            )
            .first()
        )

    def get_active_work_order_for_alert(
        self,
        alert_id: int,
    ) -> Optional[Dict]:
        """
        Return the active Work Order related to an Alert.

        This method is used by AlertsPage.
        """

        db: Session = SessionLocal()

        try:
            alert = (
                db.query(AlertModel)
                .filter(AlertModel.id == alert_id)
                .first()
            )

            if not alert:
                return None

            work_order = self._find_active_work_order_for_alert(
                db=db,
                alert=alert,
            )

            if not work_order:
                return None

            return {
                "id": work_order.id,
                "equipment_id": work_order.equipment_id,
                "equipment_name": work_order.equipment_name,
                "title": work_order.title,
                "description": work_order.description,
                "priority": work_order.priority,
                "status": work_order.status,
                "assigned_to": work_order.assigned_to,
                "created_at": work_order.created_at,
                "due_date": work_order.due_date,
                "completed_at": work_order.completed_at,
            }

        except Exception as error:
            print(
                f"Error finding Work Order for Alert "
                f"#{alert_id}: {error}"
            )
            return None

        finally:
            db.close()

    # ------------------------------------------------------------------
    # Manual Work Order creation
    # ------------------------------------------------------------------

    def create_work_order_for_alert(
        self,
        alert_id: int,
    ) -> Optional[Dict]:
        """
        Manually create a Work Order for a High or Critical Alert.

        Returns:
            A dictionary containing the Work Order data,
            or None if creation failed.
        """

        db: Session = SessionLocal()

        try:
            alert = (
                db.query(AlertModel)
                .filter(AlertModel.id == alert_id)
                .first()
            )

            if not alert:
                print(f"Alert #{alert_id} was not found.")
                return None

            if alert.severity not in ("High", "Critical"):
                print(
                    f"Work Order cannot be created for "
                    f"{alert.severity} Alert #{alert_id}."
                )
                return None

            equipment = (
                db.query(EquipmentModel)
                .filter(
                    EquipmentModel.id == alert.equipment_id
                )
                .first()
            )

            if not equipment:
                print(
                    f"Equipment '{alert.equipment_id}' was not found."
                )
                return None

            existing_work_order = (
                self._find_active_work_order_for_alert(
                    db=db,
                    alert=alert,
                )
            )

            if existing_work_order:
                db.commit()

                return {
                    "id": existing_work_order.id,
                    "equipment_id": existing_work_order.equipment_id,
                    "equipment_name": existing_work_order.equipment_name,
                    "title": existing_work_order.title,
                    "priority": existing_work_order.priority,
                    "status": existing_work_order.status,
                    "created_at": existing_work_order.created_at,
                    "due_date": existing_work_order.due_date,
                }

            # For manually created Work Orders, the title is adjusted
            # so that the relationship remains clear.
            work_order = WorkOrderModel(
                equipment_id=equipment.id,
                equipment_name=equipment.name,
                title=f"Alert Follow-up: {alert.alert_type}",
                description=(
                    f"Manually created from Alert #{alert.id}.\n\n"
                    f"Equipment: {equipment.name} ({equipment.id})\n"
                    f"Alert Type: {alert.alert_type}\n"
                    f"Severity: {alert.severity}\n"
                    f"Message: {alert.message}\n\n"
                    "Investigate the alert and document the maintenance action."
                ),
                priority=(
                    "High"
                    if alert.severity == "Critical"
                    else "Medium"
                ),
                status="Open",
                assigned_to=None,
                created_at=datetime.now(),
                due_date=datetime.now() + timedelta(hours=24),
                completed_at=None,
            )

            db.add(work_order)
            db.commit()
            db.refresh(work_order)

            print(
                f"Manual Work Order #{work_order.id} created "
                f"for Alert #{alert.id}."
            )

            return {
                "id": work_order.id,
                "equipment_id": work_order.equipment_id,
                "equipment_name": work_order.equipment_name,
                "title": work_order.title,
                "priority": work_order.priority,
                "status": work_order.status,
                "created_at": work_order.created_at,
                "due_date": work_order.due_date,
            }

        except Exception as error:
            db.rollback()
            print(
                f"Error creating Work Order for Alert "
                f"#{alert_id}: {error}"
            )
            return None

        finally:
            db.close()

    # ------------------------------------------------------------------
    # Alert retrieval
    # ------------------------------------------------------------------

    def get_alerts(
        self,
        filter_severity: Optional[str] = None,
        only_open: bool = False,
    ) -> List[Dict]:
        """
        Retrieve alerts from the database.

        Args:
            filter_severity:
                Low, Medium, High, Critical, All, or None.

            only_open:
                If True, return only unacknowledged alerts.
        """

        db: Session = SessionLocal()
        results: List[Dict] = []

        try:
            query = db.query(AlertModel)

            if filter_severity and filter_severity != "All":
                query = query.filter(
                    AlertModel.severity == filter_severity
                )

            if only_open:
                query = query.filter(
                    AlertModel.is_acknowledged.is_(False)
                )

            alerts = (
                query
                .order_by(AlertModel.timestamp.desc())
                .all()
            )

            for alert in alerts:
                related_work_order = (
                    self.get_active_work_order_for_alert(alert.id)
                )

                results.append(
                    {
                        "id": alert.id,
                        "equipment_id": alert.equipment_id,
                        "equipment_name": alert.equipment_name,
                        "alert_type": alert.alert_type,
                        "severity": alert.severity,
                        "message": alert.message,
                        "timestamp": alert.timestamp,
                        "is_acknowledged": alert.is_acknowledged,
                        "acknowledged_by": alert.acknowledged_by,
                        "acknowledged_at": alert.acknowledged_at,
                        "work_order": related_work_order,
                    }
                )

            return results

        except Exception as error:
            print(f"Error fetching alerts from database: {error}")
            return []

        finally:
            db.close()

    # ------------------------------------------------------------------
    # Alert acknowledgment
    # ------------------------------------------------------------------

    def acknowledge_alert_in_db(
        self,
        alert_id: int,
        user_name: str,
    ) -> bool:
        """
        Mark an Alert as acknowledged.
        """

        db: Session = SessionLocal()

        try:
            alert = (
                db.query(AlertModel)
                .filter(AlertModel.id == alert_id)
                .first()
            )

            if not alert:
                print(f"Alert #{alert_id} was not found.")
                return False

            if alert.is_acknowledged:
                print(
                    f"Alert #{alert_id} was already acknowledged."
                )
                return False

            alert.is_acknowledged = True
            alert.acknowledged_by = user_name
            alert.acknowledged_at = datetime.now()

            db.commit()

            print(
                f"Alert #{alert_id} acknowledged by {user_name}."
            )

            return True

        except Exception as error:
            db.rollback()
            print(
                f"Error acknowledging Alert "
                f"#{alert_id}: {error}"
            )
            return False

        finally:
            db.close()

    # ------------------------------------------------------------------
    # Equipment synchronization
    # ------------------------------------------------------------------

    @staticmethod
    def _update_equipment_status(
        equipment: EquipmentModel,
        severity: str,
    ) -> None:
        """
        Update equipment status based on alert severity.

        Critical -> Critical
        High / Medium -> Warning
        Low -> Operational
        """

        normalized_severity = severity.strip().lower()

        if normalized_severity == "critical":
            equipment.status = "Critical"

        elif normalized_severity in ("high", "medium"):
            equipment.status = "Warning"

        elif normalized_severity == "low":
            # Do not downgrade a currently Critical equipment.
            if equipment.status != "Critical":
                equipment.status = "Operational"
