#db/database.py

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

DATABASE_URL = "sqlite:///./cases.db"

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Court(Base):
    __tablename__ = "courts"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    cases = relationship("Case", back_populates="court")

class Stage(Base):
    __tablename__ = "stages"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    cases = relationship("Case", back_populates="stage")

class Case(Base):
    __tablename__ = "cases"
    id = Column(Integer, primary_key=True)
    case_number = Column(String, nullable=True)
    plaintiff = Column(String, nullable=True)
    defendant = Column(String, nullable=True)
    date = Column(Date, nullable=True)

    court_id = Column(Integer, ForeignKey("courts.id"), nullable=False)
    stage_id = Column(Integer, ForeignKey("stages.id"), nullable=False)

    court = relationship("Court", back_populates="cases")
    stage = relationship("Stage", back_populates="cases")
