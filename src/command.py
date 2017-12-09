import logging


class Command(object):
    def __init__(self, pre_timeout=0, changes=None):
        self.timeout = pre_timeout
        self.changes = {} if changes is None else changes

    def set_channel(self, channel_id, pin_value):
        if channel_id in self.changes.keys():
            logging.warn("Channel already set for command: {}".format({
                'channel_id': channel_id,
                'current_value': self.changes[channel_id],
                'new_value': pin_value
            }))

        self.changes[channel_id] = pin_value

    def increase_timeout(self, t):
        self.timeout += t
