import datetime


class Sensor:
    def __init__(self, id):
        self.id = id
        self.name = f'Sensor {id}'
        self.type = 'Normal'
        self.machine_id = 'machine01'

    def delete(self):
        return True
