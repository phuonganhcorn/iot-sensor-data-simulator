from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Device(Base):
    __tablename__ = 'device'
    session = None

    id = Column(Integer, primary_key=True, autoincrement=True)
    device_id = Column(String(255))
    generation_id = Column(Integer)
    etag = Column(String(255))
    status = Column(String(255))
    connection_string = Column(String(255))
    sensors = relationship("Sensor", back_populates="device")

    def __repr__(self):
        return f"<Device(id={self.id}, device_id={self.device_id}, generation_id={self.generation_id}, etag={self.etag}, status={self.status})>"

    @staticmethod
    def get_all():
        return Device.session.query(Device).all()

    @staticmethod
    def add(device):
        new_device = Device(device_id=device.device_id, generation_id=device.generation_id,
                            etag=device.etag, status=device.status)

        Device.session.add(new_device)
        Device.session.commit()

        return new_device

    @staticmethod
    def delete(device):
        Device.session.delete(device)
        Device.session.commit()


class Sensor(Base):
    __tablename__ = 'sensor'
    session = None

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255))
    device_id = Column(Integer, ForeignKey(Device.id))
    base_value = Column(Float)
    unit = Column(String(20))
    variation_range = Column(Float)
    change_rate = Column(Float)
    interval = Column(Float)

    device = relationship(Device, back_populates='sensors')

    def __repr__(self):
        return f"<Sensor(id={self.id}, name={self.name}, device_id={self.device_id}, base_value={self.base_value}, unit={self.unit}, variation_range={self.variation_range}, change_rate={self.change_rate}, interval={self.interval})>"

    @staticmethod
    def add(name, base_value, unit, variation_range, change_rate, interval):
        new_sensor = Sensor(name=name, base_value=base_value,
                            unit=unit, variation_range=variation_range, change_rate=change_rate, interval=interval)

        Sensor.session.add(new_sensor)
        Sensor.session.commit()

        return new_sensor

    @staticmethod
    def get_all():
        return Sensor.session.query(Sensor).all()

    @staticmethod
    def delete(sensor):
        Sensor.session.delete(sensor)
        Sensor.session.commit()
