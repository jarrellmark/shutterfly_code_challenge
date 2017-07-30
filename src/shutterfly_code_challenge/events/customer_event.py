from lib import ValueAtTime
from events import BaseEvent

class CustomerEvent(BaseEvent):
    def __init__(self, input):
        self.error = False
        super().__init__(input)

        if not self.error:
            if self.verb not in ['NEW', 'UPDATE']:
                self.error = True

    def merge(self, D):
        if not self.error:
            super().merge_base(D)
            super().merge_attributes(D,
                attributes=[
                    'last_name',
                    'adr_city',
                    'adr_state'])

            if self.verb == 'NEW':
                D[self.type][self.key]['created_time'] = ValueAtTime(self.event_time, self.event_time)
