from database import Base
from sqlalchemy.orm import  Mapped, mapped_column
from sqlalchemy import Integer, String, Numeric


class Patient(Base):
    __tablename__ = "patients"
    id: Mapped[int] = mapped_column(Integer, primary_key = True)
    name: Mapped[str] = mapped_column(String(60), nullable= False)
    gender: Mapped[str] = mapped_column(String(20), nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    height: Mapped[float]= mapped_column(Numeric(5,1 ), nullable=False)
    weight: Mapped[float] = mapped_column(Numeric(5, 1), nullable=False)
    city: Mapped[str]= mapped_column(String(60), nullable=False)