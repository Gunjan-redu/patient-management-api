from database import SessionLocal
from models import Patient



db = SessionLocal()
patients = db.query(Patient).all()

for p in patients:
    print(p.id, p.name, p.city)

db.close()