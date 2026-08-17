import json

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Annotated, Literal

app = FastAPI()


class Patient(BaseModel):
    id: Annotated[int, Field(..., description="The patient id")]
    name : Annotated[str, Field(..., description="The patient name")]
    gender: Annotated[Literal["male", "female", "other"], Field(..., description="The patient gender")]
    age: Annotated[int, Field(..., description="The patient age")]
    height: Annotated[float, Field(..., description="The patient height")]
    weight: Annotated[float, Field(..., description="The patient weight")]
    city: Annotated[str, Field(..., description="The patient city")]

class UpdatePatient(BaseModel):
    name : Annotated[str | None, Field( description="The patient name")] = None
    gender: Annotated[Literal["male", "female", "other"] | None, Field(description="The patient gender")] = None
    age: Annotated[int | None, Field(description="The patient age")] = None
    height: Annotated[float | None, Field( description="The patient height")] = None
    weight: Annotated[float | None, Field(description="The patient weight")] = None
    city: Annotated[str | None, Field(description="The patient city")] = None



def load_data() -> list[dict]:
    with open("data.json", "r") as f:
        data = json.load(f)
        return data


@app.get("/")
def welcome():
    return {
        "HomePage": "welcome to the patientAPI"
    }

@app.get("/patients")
def list_patients():
    return load_data()

@app.post("/patients", status_code=201)
def create_patient(patient: Patient):

    data = load_data()


    for i in data:
        if i["id"] == patient.id:
            raise HTTPException(
                status_code=409,
                detail="Patient already exists"

            )


    data.append(patient.model_dump())

    # Save updated data
    with open("data.json", "w") as f:
        json.dump(data, f, indent=4)

    return patient



@app.get("/patients/{patient_id}")
def one_patient(patient_id: int):
    data = load_data()

    for i in data:
        if i["id"] == patient_id:
            return i

    raise HTTPException(status_code=404, detail="Patient doesn't exist")



@app.patch("/patients/{patient_id}")
def update_patient(patient_id: int, patient: UpdatePatient):
    data = load_data()

    for i in data:
        if i['id'] == patient_id:
           update_data =  patient.model_dump(exclude_unset=True)
           i.update(update_data)
           with open("data.json", 'w') as f:
               json.dump(data, f, indent=4)
           return  i

    raise HTTPException(status_code=404, detail="Patient doesnt exist")

@app.put("/patients/{patient_id}")
def changeall(patient_id: int, patient: Patient):
    data = load_data()

    for i in data:
        if i['id'] == patient_id:
            p = patient.model_dump()
            p["id"] = patient_id
            i.update(p)
            with open("data.json", 'w') as f:
                json.dump(data, f, indent=4)
            return i

    raise HTTPException(status_code=404, detail="Patient doesn't exist")


@app.delete("/patients/{patient_id}")
def delete_patient(patient_id :int):
    data = load_data()

    for i in data:
        if i["id"] == patient_id:
            data.remove(i)
            with open("data.json", "w") as f:
                json.dump(data, f, indent=4)
            return {"Patient deleted": "done"}
    raise HTTPException(status_code=404, detail= "Patient doesn't exist")