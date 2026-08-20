"""
Database configuration and session management.
Developed by Ashkan Motaei.
"""

from sqlalchemy import create_engine, Column, String, Float, DateTime, Integer, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime

DATABASE_URL = "sqlite:///industrial_pulse.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- Model for factory assets ---
class EquipmentModel(Base):
    """Database model for factory assets."""
    __tablename__ = "equipment"
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    location = Column(String, nullable=False)
    status = Column(String, default="Operational")
    health_score = Column(Float, default=100.0)
    last_service = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    alerts = relationship("AlertModel", back_populates="equipment")
    work_orders = relationship("WorkOrderModel", back_populates="equipment")

# --- Model for system alerts ---
class AlertModel(Base):
    """Database model for system alerts."""
    __tablename__ = "alerts"
    id = Column(Integer, primary_key=True, autoincrement=True)
    equipment_id = Column(String, ForeignKey("equipment.id"), nullable=False)
    equipment_name = Column(String, nullable=False) # Denormalized for easier display
    alert_type = Column(String, nullable=False)
    severity = Column(String, default="Medium")
    message = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    is_acknowledged = Column(Boolean, default=False)
    acknowledged_by = Column(String, nullable=True)
    acknowledged_at = Column(DateTime, nullable=True)

    # Relationship to Equipment
    equipment = relationship("EquipmentModel", back_populates="alerts")

# --- Model for maintenance work orders ---
class WorkOrderModel(Base):
    """Database model for maintenance work orders."""
    __tablename__ = "work_orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    equipment_id = Column(String, ForeignKey("equipment.id"), nullable=False)
    equipment_name = Column(String, nullable=False) # Denormalized for easier display
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    priority = Column(String, default="Medium") # Low, Medium, High
    status = Column(String, default="Open") # Open, In Progress, Pending, Completed, Cancelled
    assigned_to = Column(String, nullable=True) # User name or ID
    created_at = Column(DateTime, default=datetime.utcnow)
    due_date = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Relationship to Equipment
    equipment = relationship("EquipmentModel", back_populates="work_orders")


def init_db() -> None:
    """Initialize database and seed initial data if empty."""
    Base.metadata.create_all(bind=engine)
    
    session = SessionLocal()
    # Seed Equipment if empty
    if session.query(EquipmentModel).count() == 0:
        initial_assets = [
            EquipmentModel(id="EQ-001", name="Main Compressor 01", type="Compressor", location="Zone A - Power Room", status="Operational", health_score=94.5, last_service=datetime(2026, 7, 10)),
            EquipmentModel(id="EQ-002", name="Steam Boiler Beta", type="Boiler", location="Zone B - Thermal Dep.", status="Warning", health_score=78.2, last_service=datetime(2026, 8, 1)),
            EquipmentModel(id="EQ-003", name="CNC Milling Machine 03", type="CNC", location="Zone A - Machining", status="Operational", health_score=98.0, last_service=datetime(2026, 6, 15)),
            EquipmentModel(id="EQ-004", name="Rotary Packaging Line", type="Packaging", location="Zone C - Assembly", status="Critical", health_score=45.0, last_service=datetime(2026, 8, 12)),
            EquipmentModel(id="EQ-005", name="Water Cooling Pump 02", type="Pump", location="Zone B - Infrastructure", status="Operational", health_score=91.0, last_service=datetime(2026, 5, 20)),
        ]
        session.add_all(initial_assets)
        session.commit()
    
    # Seed initial alerts if empty
    if session.query(AlertModel).count() == 0:
        initial_alerts = [
            AlertModel(equipment_id="EQ-002", equipment_name="Steam Boiler Beta", alert_type="Overheating", severity="High", message="Temperature exceeded threshold of 85°C.", timestamp=datetime(2026, 8, 14, 9, 30, 0)),
            AlertModel(equipment_id="EQ-004", equipment_name="Rotary Packaging Line", alert_type="Mechanical Failure", severity="Critical", message="Actuator motor failure detected.", timestamp=datetime(2026, 8, 14, 10, 15, 0), is_acknowledged=True, acknowledged_by="Operator A", acknowledged_at=datetime(2026, 8, 14, 10, 20, 0)),
            AlertModel(equipment_id="EQ-001", equipment_name="Main Compressor 01", alert_type="Low Oil Pressure", severity="Medium", message="Oil pressure dropped below 2 bar.", timestamp=datetime(2026, 8, 14, 11, 0, 0)),
        ]
        session.add_all(initial_alerts)
        session.commit()

    # Seed initial work orders if empty
    if session.query(WorkOrderModel).count() == 0:
        # Get equipment objects to link them correctly
        comp1 = session.query(EquipmentModel).filter_by(id="EQ-001").first()
        boiler = session.query(EquipmentModel).filter_by(id="EQ-002").first()
        cnc3 = session.query(EquipmentModel).filter_by(id="EQ-003").first()

        initial_work_orders = [
    WorkOrderModel(
        equipment_id=comp1.id,
        equipment_name=comp1.name,
        title="Check Compressor Oil Level",
        description="Inspect oil level and viscosity. Top up if needed.",
        priority="Medium",
        status="Open",
        assigned_to="Technician 1",
        due_date=datetime(2026, 8, 16),
    ),
    WorkOrderModel(
        equipment_id=boiler.id,
        equipment_name=boiler.name,
        title="Boiler Pressure Calibration",
        description="Recalibrate pressure sensors for Steam Boiler Beta.",
        priority="High",
        status="In Progress",
        assigned_to="Technician 2",
        created_at=datetime(2026, 8, 13),
        due_date=datetime(2026, 8, 15),
    ),
    WorkOrderModel(
        equipment_id=cnc3.id,
        equipment_name=cnc3.name,
        title="Routine Maintenance - CNC 03",
        description="Lubricate moving parts and check tool alignment.",
        priority="Low",
        status="Completed",
        assigned_to="Technician 3",
        due_date=datetime(2026, 8, 10),
        completed_at=datetime(2026, 8, 9),
    ),
    WorkOrderModel(
        equipment_id=comp1.id,
        equipment_name=comp1.name,
        title="Vibration Analysis Check",
        description="Perform detailed vibration analysis on compressor.",
        priority="High",
        status="Pending",
        assigned_to="Analyst 1",
        due_date=datetime(2026, 8, 18),
    ),
]

        session.add_all(initial_work_orders)
        session.commit()
        
    session.close()
