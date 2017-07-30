from lib import ValueAtTime
from events import BaseEvent

class ImageUploadEvent(BaseEvent):
    def __init__(self, input):
        self.error = False
        super().__init__(input)

        if not self.error:
            if self.verb not in ['UPLOAD']:
                self.error = True
            if not 'customer_id' in input:
                self.error = True

    def merge(self, D):
        if not self.error:
            super().merge_base(D)
            super().merge_attributes(D,
                attributes=[
                    'customer_id',
                    'camera_make',
                    'camera_model'])

            if self.verb == 'UPLOAD':
                D[self.type][self.key]['created_time'] = ValueAtTime(self.event_time, self.event_time)
