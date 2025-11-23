#!/usr/bin/env python3
"""
Populate database with sample clinical trial data for demo purposes.
"""

import asyncio
import json
from datetime import datetime
from database import Database

async def populate_database():
    """Load sample data and populate the database"""

    # Initialize database
    db = Database()
    await db.init_db()

    print("\n" + "=" * 60)
    print("📊 POPULATING DATABASE WITH SAMPLE DATA")
    print("=" * 60)

    # Load sample data
    with open('sample_data.json', 'r') as f:
        data = json.load(f)

    trial_info = data['trial_info']
    entries = data['entries']

    print(f"\n📋 Trial: {trial_info['trial_name']} (#{trial_info['trial_id']})")
    print(f"👤 Patient: {trial_info['patient_name']} (ID: {trial_info['patient_id']})")
    print(f"🏥 Site: {trial_info['site']}")
    print(f"📅 Enrolled: {trial_info['enrollment_date']}")
    print(f"\n📝 Loading {len(entries)} entries...\n")

    # Insert entries
    for i, entry_data in enumerate(entries, 1):
        # Parse timestamp
        timestamp = datetime.fromisoformat(entry_data['timestamp'].replace('Z', '+00:00'))

        # Create entry
        entry = await db.add_entry(
            transcript=entry_data['transcript'],
            patient_id=trial_info['patient_id'],
            medications_taken=entry_data.get('medications_taken', []),
            symptoms=entry_data.get('symptoms', []),
            side_effects=entry_data.get('side_effects', []),
            quality_of_life=entry_data.get('quality_of_life', {}),
            adherence_status=entry_data.get('adherence_status', 'unknown'),
            clinical_summary=entry_data.get('clinical_summary', ''),
            raw_data=entry_data
        )

        # Override timestamp with the one from sample data
        from sqlalchemy import update
        async with db.SessionLocal() as session:
            from database import ClinicalEntry
            stmt = update(ClinicalEntry).where(ClinicalEntry.id == entry.id).values(timestamp=timestamp)
            await session.execute(stmt)
            await session.commit()

        print(f"   ✅ Entry {i}/{len(entries)}: {timestamp.strftime('%Y-%m-%d %H:%M')} - {entry_data['clinical_summary'][:60]}...")

    print("\n" + "=" * 60)
    print("✅ DATABASE POPULATED SUCCESSFULLY")
    print("=" * 60)
    print(f"\n📊 Total entries: {len(entries)}")
    print(f"📅 Date range: {entries[-1]['timestamp'][:10]} to {entries[0]['timestamp'][:10]}")
    print(f"\n🌐 View dashboard at: http://localhost:8000")
    print("\n")

if __name__ == "__main__":
    asyncio.run(populate_database())
