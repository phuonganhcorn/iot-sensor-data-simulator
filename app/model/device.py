from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///telemetry_simulator.db', echo=True)

Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()


class Device(Base):
    __tablename__ = 'device'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255))
    connection_string = Column(String(255))

    def __repr__(self):
        return f"<Device(name={self.name}, connection_type={self.connection_type})>"

    @staticmethod
    def get_all():
        return session.query(Device).all()

    @staticmethod
    def add(name, connection_string):
        new_device = Device(name=name, connection_string=connection_string)

        session.add(new_device)
        session.commit()

        return new_device

    @staticmethod
    def delete(device):
        session.delete(device)
        session.commit()


# Create the table on first run
# Base.metadata.create_all(engine)
