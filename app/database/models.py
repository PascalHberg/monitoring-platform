from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.database.connection import Base

class Host(Base):
    __tablename__ = "hosts"

    id = Column(Integer, primary_key=True, index=True)
    hostname = Column(String, index=True)
    ip_address = Column(String, unique=True, index=True)
    os_type = Column(String, default="Unknown")  # Windows, Linux, Network Device
    status = Column(String, default="Offline")    # Online, Offline
    last_seen = Column(DateTime, default=datetime.utcnow)