from lib import ValueAtTime

import dateparser

class BaseEvent:
    def __init__(self, input):
        self.error = False

        if not isinstance(input, dict):
            self.error = True
        else:
            if not ('verb' in input
                    and 'key' in input
                    and 'type' in input
                    and 'event_time' in input):
                self.error = True
            self.key = input.get('key')

            try:
                self.event_time = dateparser.parse(input.get('event_time'))
            except Exception as exception:
                self.error = True

            self.verb = input.get('verb')

            self.type = input.get('type')
            if self.type not in ['CUSTOMER', 'SITE_VISIT', 'IMAGE_UPLOAD', 'ORDER']:
                self.error = True

            self.input = input

    def merge(self, D):
        pass

    def merge_base(self, D):
        if not self.error:
            if D == None:
                D = {}
            if self.type not in D:
                D[self.type] = {}

            D_model = D[self.type].get(self.key)
            if D_model == None:
                D_model = {
                    'type': ValueAtTime(self.type, self.event_time),
                    'event_time': ValueAtTime(self.event_time, self.event_time)
                }
            else:
                if self.event_time > D_model['event_time'].time:
                    D_model['event_time'] = ValueAtTime(self.event_time, self.event_time)
            D[self.type][self.key] = D_model

    def merge_attributes(self, D, attributes):
        if not self.error:
            D_model = D[self.type][self.key]
            for attribute in attributes:
                if attribute in self.input:
                    if attribute not in D_model:
                        D_model[attribute] = ValueAtTime(self.input[attribute], self.event_time)
                    else:
                        if self.event_time > D_model[attribute].time:
                            D_model[attribute] = ValueAtTime(self.input[attribute], self.event_time)
            D[self.type][self.key] = D_model
