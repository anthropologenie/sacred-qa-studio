from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
import uuid
from ..core.database import Base


class QALog(Base):
    __tablename__ = "qa_logs"
    __table_args__ = {"schema": "app"}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id = Column(String(100))
    model = Column(String(100))
    device = Column(String(50))
    request_json = Column(JSONB)
    response_json = Column(JSONB)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
