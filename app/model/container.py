import datetime

class Container:
    def __init__(self, id):
        self.id = id
        self.name = f'Container {id}'
        self.devices = []
        self.is_active = False
        self.start_time = None
        self.message_count = 0

    def start_container(self):
        self.active = True
        self.starttime = datetime.datetime.now()

    def stop_container(self):
        self.active = False
        self.starttime = None