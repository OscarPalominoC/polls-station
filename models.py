from sqlalchemy import Boolean, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Voter(Base):
    __tablename__ = "voters"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    lastname = Column(String)
    document_id = Column(Integer)
    gender = Column(String)
    has_voted = Column(Boolean, default=False)
    
    cities_id = Column(Integer, ForeignKey("cities.id"))
    cities = relationship("Cities", back_populates="voters")
    candidates = relationship("Candidate", back_populates="voters")
    

class Candidate(Base):
    __tablename__ = "candidates"
    
    id = Column(Integer, primary_key=True, index=True)
    is_candidate = Column(Boolean, default=True)
    affiliation = Column(String)
    
    voters_id = Column(Integer, ForeignKey("voters.id"))
    voters = relationship("Voter", back_populates="candidates")
    

class Cities(Base):
    __tablename__ = "cities"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    voters = relationship("Voter", back_populates="cities")
    polls = relationship("PollingStation", back_populates="cities")

class PollingStation(Base):
    __tablename__ = "polls"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    cities_id = Column(Integer, ForeignKey("cities.id"))
    cities = relationship("Cities", back_populates="polls")