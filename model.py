from pydantic import BaseModel
from typing import Dict
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./sql_app.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class StringAnalysis(Base):
    __tablename__ = "string_analysis"

    id = Column(String, primary_key=True, index=True) # sha256_hash
    value = Column(String, index=True)
    length = Column(Integer)
    is_palindrome = Column(Boolean)
    unique_characters = Column(Integer)
    word_count = Column(Integer)
    sha256_hash = Column(String, unique=True, index=True)
    character_frequency_map = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

class AnalysisRequest(BaseModel):
    value: str

class AnalysisProperties(BaseModel):
    length: int
    is_palindrome: bool
    unique_characters: int
    word_count: int
    sha256_hash: str
    character_frequency_map: Dict[str, int]

class AnalysisResponse(BaseModel):
    id: str
    value: str
    properties: AnalysisProperties
    created_at: datetime
