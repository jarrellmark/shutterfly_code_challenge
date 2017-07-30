from lib import ValueAtTime
from events import BaseEvent

class OrderEvent(BaseEvent):
    def __init__(self, input):
        self.error = False
        super().__init__(input)

        if not self.error:
            if self.verb not in ['NEW', 'UPDATE']:
                self.error = True
            if not ('total_amount' in input
                    and 'customer_id' in input):
                self.error = True
            try:
                self.input['total_amount'] = float(str(self.input['total_amount']).split(' ')[0])
            except Exception as exception:
                self.error = True

    def merge(self, D):
        if not self.error:
            super().merge_base(D)
            super().merge_attributes(D,
                attributes=[
                    'customer_id',
                    'total_amount'])

            if self.verb == 'NEW':
                D[self.type][self.key]['created_time'] = ValueAtTime(self.event_time, self.event_time)
