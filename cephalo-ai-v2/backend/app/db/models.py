from datetime import datetime
from sqlalchemy import String, DateTime, Float, Integer, ForeignKey, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base

class Case(Base):
    __tablename__ = 'cases'
    id: Mapped[int] = mapped_column(primary_key=True)
    patient_code: Mapped[str] = mapped_column(String(80), default='DEMO')
    image_path: Mapped[str] = mapped_column(String(500))
    image_width: Mapped[int] = mapped_column(Integer)
    image_height: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    landmarks: Mapped[list] = mapped_column(JSON, default=list)
    ground_truth: Mapped[list | None] = mapped_column(JSON, nullable=True)
    initial_landmarks: Mapped[list | None] = mapped_column(JSON, nullable=True)
    evaluation: Mapped[dict] = mapped_column(JSON, default=dict)
    measurements: Mapped[dict] = mapped_column(JSON, default=dict)
    history: Mapped[list] = mapped_column(JSON, default=list)
