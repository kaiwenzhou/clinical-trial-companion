from sqlalchemy import Column, Integer, String, DateTime, JSON, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from datetime import datetime
from typing import List, Optional
import json

Base = declarative_base()

class ClinicalEntry(Base):
    __tablename__ = "clinical_entries"

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    transcript = Column(Text)
    symptoms = Column(JSON)  # List of symptoms
    medications = Column(JSON)  # List of medications
    side_effects = Column(JSON)  # List of side effects
    raw_data = Column(JSON)  # Full Omi payload

    def to_dict(self):
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "transcript": self.transcript,
            "symptoms": self.symptoms or [],
            "medications": self.medications or [],
            "side_effects": self.side_effects or [],
        }

class Database:
    def __init__(self, db_url: str = "sqlite+aiosqlite:///./clinical_trial.db"):
        self.engine = create_async_engine(db_url, echo=False)
        self.SessionLocal = sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )

    async def init_db(self):
        """Initialize database tables"""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✅ Database initialized")

    async def add_entry(
        self,
        transcript: str,
        symptoms: List[str],
        medications: List[str],
        side_effects: List[str],
        raw_data: dict
    ) -> ClinicalEntry:
        """Add a new clinical entry"""
        async with self.SessionLocal() as session:
            entry = ClinicalEntry(
                transcript=transcript,
                symptoms=symptoms,
                medications=medications,
                side_effects=side_effects,
                raw_data=raw_data
            )
            session.add(entry)
            await session.commit()
            await session.refresh(entry)
            return entry

    async def get_all_entries(self) -> List[ClinicalEntry]:
        """Get all clinical entries"""
        async with self.SessionLocal() as session:
            from sqlalchemy import select
            result = await session.execute(
                select(ClinicalEntry).order_by(ClinicalEntry.timestamp.desc())
            )
            return result.scalars().all()
