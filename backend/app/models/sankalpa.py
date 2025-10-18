from sqlalchemy import Column, String, Text, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from ..core.database import Base


class Sankalpa(Base):
    """
    Sankalpa (intention/resolve) model for storing spiritual commitments and intentions.
    """
    __tablename__ = "sankalpa"
    __table_args__ = {"schema": "app"}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    text = Column(Text, nullable=False)
    context = Column(Text, nullable=True)
    status = Column(String(50), default="active", index=True)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self):
        return f"<Sankalpa(id={self.id}, text='{self.text[:30] if len(self.text) > 30 else self.text}', status='{self.status}')>"
