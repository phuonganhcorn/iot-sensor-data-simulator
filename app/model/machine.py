class Machine:
    def __init__(self, id):
        self.id = id
        self.name = f'Machine {id}'

    def delete(self):
        return True
