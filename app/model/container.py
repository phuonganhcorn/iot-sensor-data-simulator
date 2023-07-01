import datetime


class Container:
    def __init__(self, id):
        self.id = id
        self.name = f'Container {id}'
        self.devices = []
        self.is_active = False
        self.start_time = None
        self.message_count = 0

    def start(self):
        if self.is_active:
            return False

        self.is_active = True
        self.start_time = datetime.datetime.now()
        return True

    def stop(self):
        if not self.is_active:
            return False

        self.is_active = False
        self.start_time = None
        return True

    def delete(self):
        self.stop()
        return True
