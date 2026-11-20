from datetime import datetime

from sqlalchemy import DateTime, Float, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base


class Investigation(Base):
    __tablename__ = "investigations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    sanitized_input: Mapped[str] = mapped_column(Text)
    service_name: Mapped[str] = mapped_column(String(255))
    error_type: Mapped[str] = mapped_column(String(255))
    top_hypothesis_cause: Mapped[str | None] = mapped_column(Text, nullable=True)
    top_hypothesis_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    report_markdown: Mapped[str | None] = mapped_column(Text, nullable=True)
    warnings: Mapped[str] = mapped_column(Text, default="[]")
    status: Mapped[str] = mapped_column(String(20))

    feedback: Mapped[list["Feedback"]] = relationship(
        back_populates="investigation",
        cascade="all, delete-orphan",
    )
