from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///telemetry_simulator.db', echo=True)

Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()

# Define the Sensor class representing the "sensor" table


class Sensor(Base):
    __tablename__ = 'sensor'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255))
    # device_id = Column(Integer, ForeignKey('other_table.id'))
    base_value = Column(Float)
    unit = Column(String(20))
    variation_range = Column(Float)
    change_rate = Column(Float)
    interval = Column(Float)

    def __repr__(self):
        return f"<Sensor(name={self.name}, base_value={self.base_value}, unit={self.unit}, change_rate={self.change_rate}, interval={self.interval})>"

    @staticmethod
    def add(name, base_value, unit, variation_range, change_rate, interval):
        new_sensor = Sensor(name=name, base_value=base_value,
                            unit=unit, variation_range=variation_range, change_rate=change_rate, interval=interval)

        session.add(new_sensor)
        session.commit()

        return new_sensor

    @staticmethod
    def get_all():
        return session.query(Sensor).all()

    @staticmethod
    def delete(sensor):
        session.delete(sensor)
        session.commit()

    # Establish the relationship with other_table
    # other_table = relationship("OtherTable")  # Replace "OtherTable" with the actual name of the referenced table

# Create the table on first run
# Base.metadata.create_all(engine)
