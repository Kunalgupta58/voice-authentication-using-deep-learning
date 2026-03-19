from sqlalchemy import Column, Integer, String, LargeBinary, Float
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    # Store the 192-dimensional embedding (float32 array) as binary
    embedding = Column(LargeBinary, nullable=False)
    # Registration confidence score if needed
    registration_score = Column(Float, nullable=True)
    
