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
    patient_id = Column(String, default="7482")  # Patient identifier
    transcript = Column(Text)

    # Enhanced structured data from Claude
    medications_taken = Column(JSON)  # [{"name": "...", "time": "...", "dose": "..."}]
    symptoms = Column(JSON)  # [{"name": "...", "severity": "...", "onset_time": "..."}]
    side_effects = Column(JSON)  # [{"symptom": "...", "relation_to_drug": "..."}]
    quality_of_life = Column(JSON)  # {"energy_level": "...", "work_capacity": "..."}
    adherence_status = Column(String)  # "compliant", "non-compliant"
    clinical_summary = Column(Text)  # AI-generated summary

    raw_data = Column(JSON)  # Full Omi payload

    def to_dict(self):
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "patient_id": self.patient_id,
            "transcript": self.transcript,
            "medications_taken": self.medications_taken or [],
            "symptoms": self.symptoms or [],
            "side_effects": self.side_effects or [],
            "quality_of_life": self.quality_of_life or {},
            "adherence_status": self.adherence_status,
            "clinical_summary": self.clinical_summary,
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
        patient_id: str = "7482",
        medications_taken: Optional[List[dict]] = None,
        symptoms: Optional[List[dict]] = None,
        side_effects: Optional[List[dict]] = None,
        quality_of_life: Optional[dict] = None,
        adherence_status: Optional[str] = None,
        clinical_summary: Optional[str] = None,
        raw_data: Optional[dict] = None
    ) -> ClinicalEntry:
        """Add a new clinical entry"""
        async with self.SessionLocal() as session:
            entry = ClinicalEntry(
                transcript=transcript,
                patient_id=patient_id,
                medications_taken=medications_taken or [],
                symptoms=symptoms or [],
                side_effects=side_effects or [],
                quality_of_life=quality_of_life or {},
                adherence_status=adherence_status,
                clinical_summary=clinical_summary,
                raw_data=raw_data or {}
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
