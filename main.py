from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Annotated, Literal
from models import Patient as PatientDB
from database import SessionLocal
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

app = FastAPI()

class PatientCreate(BaseModel):
    name: Annotated[str, Field(..., description="The patient name")]
    gender: Annotated[Literal["male", "female", "other"], Field(..., description="The patient gender")]
    age: Annotated[int, Field(..., gt=0, lt=120, description="The patient age")]
    height: Annotated[float, Field(..., gt=30, lt=272, description="Height in cm")]
    weight: Annotated[float, Field(..., gt=1, lt=500, description="Weight in kg")]
    city: Annotated[str, Field(..., description="The patient city")]


class Patient(PatientCreate):
    id: Annotated[int, Field(..., description="The patient id")]


class UpdatePatient(BaseModel):
    name : Annotated[str | None, Field( description="The patient name")] = None
    gender: Annotated[Literal["male", "female", "other"] | None, Field(description="The patient gender")] = None
    age: Annotated[int | None, Field(gt=0, lt=120, description="The patient age")] = None
    height: Annotated[float | None, Field(gt=30, lt=272, description="Height in cm")] = None
    weight: Annotated[float | None, Field(gt=1, lt=500, description="Weight in kg")] = None
    city: Annotated[str | None, Field(description="The patient city")] = None



def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()

@app.get("/")
def welcome():
    return {
        "HomePage": "welcome to the patientAPI"
    }

@app.get("/patients")
def list_patients(db:Session = Depends(get_db)):
    return db.query(PatientDB).all()

@app.post("/patients", status_code=201)
def create_patient(patient: PatientCreate, db: Session = Depends(get_db)):
    newpatient =  PatientDB(**patient.model_dump())
    db.add(newpatient)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=422, detail="Patient data violates database constraints")
    db.refresh(newpatient)
    return newpatient



@app.get("/patients/{patient_id}")
def one_patient(patient_id: int, db:Session = Depends(get_db)):
    patient =    db.query(PatientDB).filter(PatientDB.id == patient_id).first()
    if not patient:
         raise HTTPException(status_code=404, detail="Patient doesn't exist")

    return patient


@app.patch("/patients/{patient_id}")
def update_patient(patient_id: int, patientU: UpdatePatient, db:Session= Depends(get_db)):
    patient = db.query(PatientDB).filter(PatientDB.id == patient_id).first()

    if not patient:
        raise HTTPException(status_code=404, detail="Patient doesnt exist")

    for key, value in patientU.model_dump(exclude_unset=True).items():
        setattr(patient, key, value)
    db.commit()
    db.refresh(patient)
    return patient


@app.put("/patients/{patient_id}")
def replace_patient(patient_id: int, patientU: PatientCreate, db:Session = Depends(get_db)):
    patient = db.query(PatientDB).filter(PatientDB.id == patient_id).first()

    if not patient:
        raise HTTPException(status_code=404, detail="Patient doesn't exist")
    for key, value in patientU.model_dump().items():
        setattr(patient, key, value)
    db.commit()
    db.refresh(patient)
    return patient


@app.delete("/patients/{patient_id}")
def delete_patient(patient_id :int, db:Session = Depends(get_db) ):
    patient = db.query(PatientDB).filter(PatientDB.id == patient_id).first()

    if not patient:
        raise HTTPException(status_code=404, detail= "Patient doesn't exist")

    db.delete(patient)
    db.commit()
    return {"Request Processed": "Patient Deleted"}