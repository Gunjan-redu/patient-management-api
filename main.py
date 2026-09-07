from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Annotated, Literal
from models import Patient as PatientDB
from models import Appointment
from database import SessionLocal
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from pydantic import ConfigDict


app = FastAPI()

class PatientCreate(BaseModel):
    name: Annotated[str, Field(..., description="The patient name")]
    gender: Annotated[Literal["male", "female", "other"], Field(..., description="The patient gender")]
    age: Annotated[int, Field(..., gt=0, lt=120, description="The patient age")]
    height: Annotated[float, Field(..., gt=30, lt=272, description="Height in cm")]
    weight: Annotated[float, Field(..., gt=1, lt=500, description="Weight in kg")]
    city: Annotated[str, Field(..., description="The patient city")]


class Patient(PatientCreate):
    model_config = ConfigDict(from_attributes=True)
    id: Annotated[int, Field(..., description="The patient id")]


class UpdatePatient(BaseModel):
    name : Annotated[str | None, Field( description="The patient name")] = None
    gender: Annotated[Literal["male", "female", "other"] | None, Field(description="The patient gender")] = None
    age: Annotated[int | None, Field(gt=0, lt=120, description="The patient age")] = None
    height: Annotated[float | None, Field(gt=30, lt=272, description="Height in cm")] = None
    weight: Annotated[float | None, Field(gt=1, lt=500, description="Weight in kg")] = None
    city: Annotated[str | None, Field(description="The patient city")] = None




class AppointmentCreate(BaseModel):
    appt_at: Annotated[datetime,Field(..., description="Date and time of appointment") ]
    reason: Annotated[str, Field(...,min_length=3, max_length=200, description="Reason for the appointment ")]






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

@app.get("/patients", response_model=list[Patient])
def list_patients(
        city: str| None = None,
        min_age: int | None = None,
        sort_by: Literal["age", "weight", "height"] | None = None,
        db:Session = Depends(get_db)):

    query = db.query(PatientDB)
    if city:
        query = query.filter(PatientDB.city == city)
    if min_age:
        query = query.filter(PatientDB.age >= min_age)
    if sort_by:
        query = query.order_by(getattr(PatientDB, sort_by))


    return query.all()

@app.post("/patients", status_code=201, response_model=Patient)
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



@app.get("/patients/{patient_id}",  response_model=Patient)
def one_patient(patient_id: int, db:Session = Depends(get_db)):
    patient =    db.query(PatientDB).filter(PatientDB.id == patient_id).first()
    if not patient:
         raise HTTPException(status_code=404, detail="Patient doesn't exist")

    return patient


@app.patch("/patients/{patient_id}", response_model=Patient)
def update_patient(patient_id: int, patientU: UpdatePatient, db:Session= Depends(get_db)):
    patient = db.query(PatientDB).filter(PatientDB.id == patient_id).first()

    if not patient:
        raise HTTPException(status_code=404, detail="Patient doesnt exist")

    for key, value in patientU.model_dump(exclude_unset=True).items():
        setattr(patient, key, value)
    db.commit()
    db.refresh(patient)
    return patient


@app.put("/patients/{patient_id}", response_model=Patient)
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
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail= "Patient has appointments, remove those first.")
    return {"Request Processed": "Patient Deleted"}



@app.post("/patients/{patient_id}/appointments", status_code=201)
def book_appointment(patient_id : int, appt: AppointmentCreate, db:Session = Depends(get_db)):
    patient =db.query(PatientDB).filter(PatientDB.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    new_appt = Appointment(**appt.model_dump(), patient_id= patient_id)
    db.add(new_appt)
    db.commit()
    db.refresh(new_appt)
    return new_appt



@app.get("/patients/{patient_id}/appointments")
def get_appointments(patient_id: int, db: Session = Depends(get_db)):
    patient = db.query(PatientDB).filter(PatientDB.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="This patient does not exist")
    return db.query(Appointment).filter(Appointment.patient_id == patient_id).all()



