from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Options(Base):
    __tablename__ = 'options'
    session = None

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255))
    value = Column(String(255))

    def __repr__(self):
        return f"<Options(id={self.id}, name={self.name}, value={self.value})>"

    @staticmethod
    def get_option(name):
        return Options.session.query(Options).filter_by(name=name).first()

    @staticmethod
    def set_option(name, value):
        option = Options.get_option(name)
        if option is None:
            option = Options(name=name, value=value)
            Options.session.add(option)
        else:
            option.value = value
        Options.session.commit()
        return option


class Device(Base):
    __tablename__ = 'device'
    session = None

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255))
    generation_id = Column(Integer)
    etag = Column(String(255))
    status = Column(String(255))
    connection_string = Column(String(255))
    sensors = relationship("Sensor", back_populates="device")

    def __repr__(self):
        return f"<Device(id={self.id}, name={self.device_id}, generation_id={self.generation_id}, etag={self.etag}, status={self.status})>"

    @staticmethod
    def get_all():
        return Device.session.query(Device).all()

    @staticmethod
    def store(device):
        primary_key = device.authentication.symmetric_key.primary_key
        host_name = Options.get_option('host_name').value
        connection_string = f"HostName={host_name};DeviceId={device.device_id};SharedAccessKey={primary_key}"

        device_db = Device(name=device.device_id, generation_id=device.generation_id,
                           etag=device.etag, status=device.status, connection_string=connection_string)

        Device.session.add(device_db)
        Device.session.commit()

        return device_db

    @staticmethod
    def delete(device):
        Device.session.delete(device)
        Device.session.commit()


class Sensor(Base):
    __tablename__ = 'sensor'
    session = None

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255))
    base_value = Column(Float)
    unit = Column(String(20))
    variation_range = Column(Float)
    change_rate = Column(Float)
    interval = Column(Float)
    device_id = Column(Integer, ForeignKey(Device.id))

    device = relationship(Device, back_populates='sensors')

    def __repr__(self):
        return f"<Sensor(id={self.id}, name={self.name}, base_value={self.base_value}, unit={self.unit}, variation_range={self.variation_range}, change_rate={self.change_rate}, interval={self.interval}, device_id={self.device_id})>"

    @staticmethod
    def add(name, base_value, unit, variation_range, change_rate, interval, device_id):
        new_sensor = Sensor(name=name, base_value=base_value,
                            unit=unit, variation_range=variation_range, change_rate=change_rate, interval=interval, device_id=device_id)

        Sensor.session.add(new_sensor)
        Sensor.session.commit()

        return new_sensor

    @staticmethod
    def get_all():
        return Sensor.session.query(Sensor).all()

    @staticmethod
    def get_all_by_ids(list_of_ids):
        return Sensor.session.query(Sensor).filter(Sensor.id.in_(list_of_ids)).all()

    # Returns all sensors that are not assigned to a device
    @staticmethod
    def get_all_unassigned():
        return Sensor.session.query(Sensor).filter(Sensor.device_id == None).all()

    @staticmethod
    def delete(sensor):
        Sensor.session.delete(sensor)
        Sensor.session.commit()
