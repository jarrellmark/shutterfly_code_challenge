class ValueAtTime:
    def __init__(self, value, time):
        self.value = value
        self.time = time

    def __repr__(self):
        return "{value} at {time}".format(
            value=self.value,
            time=self.time)
